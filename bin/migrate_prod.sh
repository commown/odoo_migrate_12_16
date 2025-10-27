#!/bin/sh

CURRENT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
ODOO_MIGRATE_DIR=$(dirname "$CURRENT_DIR")

DB_NAME=odoo_commown
PG_DOCKER_NAME=commown-12-16-container-postgres-11
ODOO_DOCKER_NAME=odoo-openupgrade-wizard-image__commown-12-16__12.0

BORG_REPO='ssh://dg47j6im@dg47j6im.repo.borgbase.com/./repo'
BORG_MOUNT="$ODOO_MIGRATE_DIR"/borg_mount
DOCKER_BORG_MOUNT=/env/borg_mount

LOCAL_OUTDATED_FILESTORE="$ODOO_MIGRATE_DIR"/odoo_commown_filestore.tar

odoo_addons()
{
    sep=""
    for dir in $(ls "$ODOO_MIGRATE_DIR"/src/env_12.0/src)
    do
        echo -n "$sep"
        sep=","
        case "$dir" in
            "odoo")
                echo -n "/odoo_env/src/odoo/addons,/odoo_env/src/odoo/odoo/addons"
                ;;
            "openupgrade")
                sep=""
                ;;
            *)
                echo -n "/odoo_env/src/${dir}"
        esac
    done
}

prereqs()
{
  which rsync > /dev/null || exit 1

  if [ ! -f "$LOCAL_OUTDATED_FILESTORE" ]
  then
      echo "You need an initial filestore to speed-up restoration."
      echo "Its path must be: $LOCAL_OUTDATED_FILESTORE."
      exit 1
  fi

  [ ! -e "$BORG_MOUNT" ] && mkdir "$BORG_MOUNT"
}

bmount()
{
  if [ -z "$1" ]
  then
    archive=$(borg list --last 1 --short $BORG_REPO)
    echo "Mount last archive (${archive})..."
  else
    archive=$1
  fi
  borg mount -o allow_other,uid=$(id -u),gid=$(id -g) $BORG_REPO::${archive} $BORG_MOUNT
}

bumount()
{
  borg umount $BORG_MOUNT
}

restore() {
  # Drop db if it exists

  date
  echo "Removing existing database $DB_NAME if any..."
  oow psql -l -d postgres 2>/dev/null | grep "$DB_NAME" > /dev/null && oow dropdb -d "$DB_NAME" 2>/dev/null

  date
  echo "Mounting the backup archive locally..."
  bmount

  date
  echo "Restarting container $PG_DOCKER_NAME"...
  docker restart "$PG_DOCKER_NAME"

  sleep 10

  # Since the filestore is big, we hack its restore as follows:
  # 1. give oow restoredb an empty tar so that unarchiving is instant
  # 2. extract a local archive of the filestore, even if not recent
  # 3. rsync the backup into the destination, which should be quick enough

  BACKUP_FILESTORE_PATH=var/lib/odoo/.local/share/Odoo/filestore/odoo_commown
  BACKUP_PG_DUMP_PATH=root/.borgmatic/postgresql_databases/localhost/odoo_commown

  empty_dir=$(mktemp -d -p "$ODOO_MIGRATE_DIR")

  date
  echo "Restoring the DB backup..."

  oow restoredb -d "$DB_NAME" \
      --database-path "$BORG_MOUNT"/"$BACKUP_PG_DUMP_PATH" \
      --database-format c \
      --filestore-path "$empty_dir" \
      --filestore-format d > /dev/null 2>&1

  rmdir "$empty_dir"

  date
  echo "Extracting a local copy of the filestore..."
  rm -rf "$ODOO_MIGRATE_DIR"/filestore/filestore/"$DB_NAME"
  tar -C "$ODOO_MIGRATE_DIR" -xf "$LOCAL_OUTDATED_FILESTORE"

  date
  echo "... and synchronize its backup into it..."
  rsync -a --info=progress2 --delete \
        "$BORG_MOUNT"/"$BACKUP_FILESTORE_PATH"/ \
        "$ODOO_MIGRATE_DIR"/filestore/filestore/"$DB_NAME"/ || exit 1

  date
  echo "Done! Cleaning up..."
  bumount && docker restart "$PG_DOCKER_NAME"
}

make_safe()
{
  date
  echo "Starting an Odoo container to make the DB safe..."

  docker inspect make_odoo_db_safe > /dev/null 2>&1 && docker stop -t0 make_odoo_db_safe

  docker run -d \
         --name make_odoo_db_safe \
         --volume "$ODOO_MIGRATE_DIR":/env/ \
         --volume "$ODOO_MIGRATE_DIR"/src/env_12.0:/odoo_env/ \
         --link "$PG_DOCKER_NAME":db \
         --rm "$ODOO_DOCKER_NAME" \
         sleep infinity

  date
  echo "Starting the script to make the DB safe..."

  docker exec -i make_odoo_db_safe \
         /odoo_env/src/odoo/odoo-bin shell \
         --config=/odoo_env/odoo.conf \
         --data-dir=/env/filestore/ \
         --addons-path="$(odoo_addons)" \
         --logfile=/env/log/make_odoo_db_safe.log \
         --db_host=db --db_port=5432 --db_user=odoo --db_password=odoo \
         --workers=0 --without-demo=all --database="$DB_NAME" \
         < "$ODOO_MIGRATE_DIR"/bin/odoo_db_make_safe.py || exit 1

  date
  echo "Removing the container..."

  docker stop -t0 make_odoo_db_safe

  date
  echo "Done! The DB is safe"
}

migrate_0_2()
{
  # Launch the migration, step by step
  date
  echo "Saving before starting the migration..."

  oow copydb -s odoo_commown -d odoo_commown-step-0 > /dev/null 2>&1 || exit 1

  # STEP 1 and 2 (step 1 is very short)

  date
  echo "Migration: steps 1 and 2 (duration ~9h)..."

  oow upgrade --first-step 1 --last-step 2 -d odoo_commown > /dev/null 2>&1 || exit 1
  oow copydb -s odoo_commown -d odoo_commown-step-2  > /dev/null 2>&1 || exit 1

  oow dropdb -d odoo_commown-step-0 > /dev/null 2>&1 || exit 1
}

migrate_3()
{
  # STEP 3

  date
  echo "Migration: step 3 (duration ~5h)..."

  oow upgrade --first-step 3 --last-step 3 -d odoo_commown > /dev/null 2>&1 || exit 1
  oow copydb -s odoo_commown -d odoo_commown-step-3  > /dev/null 2>&1 || exit 1

  oow dropdb -d odoo_commown-step-2 > /dev/null 2>&1 || exit 1
}

migrate_4_6()
{
  # STEP 4 and 5

  date
  echo "Migration: steps 4 and 5 (duration ~5h)..."

  oow upgrade --first-step 4 --last-step 5 -d odoo_commown > /dev/null 2>&1 || exit 1
  oow copydb -s odoo_commown -d odoo_commown-step-5  > /dev/null 2>&1 || exit 1

  oow dropdb -d odoo_commown-step-3 > /dev/null 2>&1 || exit 1

  # STEP 6
  date
  echo "Migration: step 6 (duration ~5 minutes)..."

  oow upgrade --first-step 6 --last-step 6 -d odoo_commown > /dev/null 2>&1 || exit 1
  oow copydb -s odoo_commown -d odoo_commown-step-6  > /dev/null 2>&1 || exit 1

  oow dropdb -d odoo_commown-step-5 > /dev/null 2>&1 || exit 1

  date
  echo "Migration: DONE!"
}

send()
{
  # Dump the resulting DB and upload it to Hirondelle

  date
  echo "Dumping the DB and filestore for shipping..."

  oow dumpdb -d odoo_commown \
      --database-path odoo-commown-16.tar \
      --database-format t \
      --filestore-path filestore-16.tar \
      --filestore-format t > /dev/null 2>&1

  date
  echo "Shipping to destination..."

  scp odoo-commown-16.tar filestore-16.tar root@hirondelle.netbird.selfhosted:/root/

  date
  echo "Shipping: DONE!"

}

prereqs || exit 1
restore || exit 1
make_safe || exit 1
migrate_0_2 || exit 1
migrate_3 || exit 1
migrate_4_6 || exit 1
send || exit 1

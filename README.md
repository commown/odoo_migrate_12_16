# Installation d'un environnement OOW (Odoo OpenUpgrade Wizard)

1. Installez le paquet `odoo-openupgrade-wizard` : 
```sh
pipx install odoo-openupgrade-wizard
```

NOTE: l'initialisation du projet OOW a déjà été faite, 
et les fichiers concernés ont été poussés sur le dépôt `odoo_migrate_12_16`.
Il n'y a donc pas besoin de refaire `oow init`

2. Récupérez le code des différentes versions de Odoo
```sh
oow get-code
```

3. Construisez les images Docker pour les différentes versions de Odoo
```sh
oow docker-build
``` 

# Migration de base de données Odoo

## Phase de mise au point

On commence par restaurer une base sur notre instance v12 habituelle
(hors oow) avec `install_last_odoo_backup`.

Puis on se place à la racine du dépôt odoo_migrate_12_16 et :
- on récupère un pg_dump du résultat et le filestore :

```
docker exec -ti --user odoo odoo-v12 \
  bash -c 'pg_dump -U odoo -d odoo_commown -Ft' \
  > pg_dump_odoo_prod_$(date +%Y%m%d).tar
docker cp odoo-v12:/var/lib/odoo/.local/share/Odoo/filestore/odoo_commown \
  filestore/filestore/12.0-odoo-commown-init
```

On "charge" la base et le filestore dans oow :
```
oow restoredb -d 12.0-odoo-commown-step-0 \
  --database-path pg_dump_odoo_prod_$(date +%Y%m%d).tar --database-format t \
  --filestore-format d --filestore-path filestore/filestore/12.0-odoo-commown-init/
```

Et enfin on en fait une copie de travail :
```
oow copydb -s 12.0-odoo-commown-step-0 -d 12.0-odoo-commown
```


## Migration étape par étape

À chaque étape on sauvegarde le résultat (DB + filestore) :

### Étape 1

On reste en v12 mais en mettant tous les modules à jour :

```
oow upgrade --first-step 1 --last-step 1 -d 12.0-odoo-commown
oow copydb -s 12.0-odoo-commown -d 12.0-odoo-commown-step-1
```

Durée : < 3 minutes

Base de données et filestore résultat supprimés pour faire de la place
sur le disque.

### Étape 2

On migre en 13.0

```
oow upgrade --first-step 2 --last-step 2 -d 12.0-odoo-commown
oow copydb -s 12.0-odoo-commown -d 12.0-odoo-commown-step-2
```

Durée : ~ 9h

Fichier 2025_09_27__09_49_21__upgrade____step_02__openupgrade__13.0.log

Résultat :
- odoo.osv.expression: Non-stored field contract.line.display_name cannot be searched.
- vues matérialisées pour la BI vides (normal, pas grave)

### Étape 3

On migre en 14.0

```
oow upgrade --first-step 3 --last-step 3 -d 12.0-odoo-commown
oow copydb -s 12.0-odoo-commown -d 12.0-odoo-commown-step-3
```

Durée : au moins 5h

Fichier : 2025_09_27__18_48_19__upgrade____step_03__openupgrade__14.0.log

Résultat :
- CRASH avant la fin (BDD 12.0-odoo-commown-step-3-crash-2025_09_27__18_48_19)
- `Please define a payment method on your payment.`

### Étape 4

On migre en 15.0

```
oow upgrade --first-step 4 --last-step 4 -d 12.0-odoo-commown
oow copydb -s 12.0-odoo-commown -d 12.0-odoo-commown-step-4
```

Résultat :
- Plantage consécutif au précédent
  `psycopg2.errors.UndefinedColumn: column "move_type" does not exist`

### Étape 5

On migre en 16.0

```
oow upgrade --first-step 5 --last-step 5 -d 12.0-odoo-commown
oow copydb -s 12.0-odoo-commown -d 12.0-odoo-commown-step-5
```

Durée : ?

### Étape 6

On reste en 16.0

```
oow upgrade --first-step 6 --last-step 6 -d 12.0-odoo-commown
oow copydb -s 12.0-odoo-commown -d 12.0-odoo-commown-step-6
```

Durée :

Résultat :

## Préparation à la migration en production (DRAFT)

- installation d'un serveur Odoo en v16
- tests avec une base de démo et tous nos modules
- diminution drastique du TTL du DNS

## Le jour de la migration (DRAFT)

L'idéal est de faire ça la nuit pour éviter un arrêt inhabituel. En
cas d'échec on redémarre simplement la prod.

- arrêt de Odoo et du backup
- dump de la base de données
- copie (ou synchro) du filestore et de la base de données sur la machine de migration (à conserver)
- restore du tout dans oow sur la machine de migration
- copie du résultat (DB + filestore) sur le nouveau serveur odoo
- démarrage et tests, notamment avec Slimpay (attention aux appels HTML de feedback)
- si KO : on redémarre la prod v12 et on reconfigure les appels de feedback Slimpay
- si OK : on configure le DNS et c'est parti !

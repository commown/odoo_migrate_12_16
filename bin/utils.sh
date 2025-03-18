oow_docker_name() { docker ps | awk '/oow-commown/ {print $NF}'; }

oow_db_name() { 
    docker inspect $(oow_docker_name) \
    | grep -A1 -- '--database' \
    | tail -1 \
    | tr -d '", '
}

oow_module_name() { 
    docker inspect $(oow_docker_name) \
    | grep -A1 -- '--init' \
    | tail -1 \
    | tr -d '", '
}

oow_launch_test() {
    docker exec -ti $(oow_docker_name) bash -c "cd /env/src/env_16.0/src/commown-odoo-addons/$(oow_module_name)/tests && PYTHONPATH=/odoo_env/src/odoo pytest -v --odoo-config /odoo_env/odoo_test.conf --odoo-database $(oow_db_name) -s $*"
}

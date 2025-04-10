oow_addons_path() {
    echo /odoo_env/src/odoo/addons,/odoo_env/src/odoo/odoo/addons,/odoo_env/src/openupgrade,/odoo_env/src/account-budgeting,/odoo_env/src/account-financial-reporting,/odoo_env/src/account-financial-tools,/odoo_env/src/account-invoicing,/odoo_env/src/account-payment,/odoo_env/src/account-reconcile,/odoo_env/src/bank-payment,/odoo_env/src/bank-statement-import,/odoo_env/src/connector-telephony,/odoo_env/src/contract,/odoo_env/src/e-commerce,/odoo_env/src/edi,/odoo_env/src/l10n-france,/odoo_env/src/mis-builder,/odoo_env/src/partner-contact,/odoo_env/src/project,/odoo_env/src/purchase-workflow,/odoo_env/src/queue,/odoo_env/src/reporting-engine,/odoo_env/src/sale-workflow,/odoo_env/src/server-auth,/odoo_env/src/server-backend,/odoo_env/src/server-brand,/odoo_env/src/server-env,/odoo_env/src/server-tools,/odoo_env/src/server-ux,/odoo_env/src/social,/odoo_env/src/stock-logistics-workflow,/odoo_env/src/web,/odoo_env/src/website,/odoo_env/src/survey,/odoo_env/src/odoo-usability,/odoo_env/src/commown-odoo-addons
}

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
    docker exec -ti $(oow_docker_name) bash -c "cd /env/src/env_16.0/src/*/$(oow_module_name)/tests && PYTHONPATH=/odoo_env/src/odoo pytest -v --odoo-config /odoo_env/odoo_test.conf --odoo-database $(oow_db_name) -s $*"
}

oow_run_odoo_with_all_ported_modules() {
   oow run -s 6 --with-demo -d test_16.0_all -i $(oow_all_ported_modules)
}

oow_all_ported_modules() {
  ls src/env_16.0/src/commown-odoo-addons/*/__manifest__.py | awk -F/ '{print $5}' | tr '\n' ','
}

oow_launch_test_all() {
    module=$1
    shift
    docker exec -ti $(oow_docker_name) bash -c "cd /env/src/env_16.0/src/*/${module}/tests && PYTHONPATH=/odoo_env/src/odoo pytest -v --odoo-config /odoo_env/odoo_test.conf --odoo-database test_16.0_all -s $*"
}

oow_shell() {
    docker exec -ti $(oow_docker_name) bash -c "PYTHONPATH=/odoo_env/src/odoo /odoo_env/src/odoo/odoo-bin shell --config=/odoo_env/odoo.conf --data-dir=/env/filestore/ --addons-path=$(oow_addons_path) --db_host=db --db_port=5432 --db_user=odoo --db_password=odoo --workers=0 --database $(oow_db_name)"
}

oow_bash() {
    docker exec -ti $* $(oow_docker_name) bash
}

oow_last_log() {
    echo log/$(ls log | tail -n 1)
}

oow_field_mig_info() {
    fieldname=$1
    grep -w $fieldname ./src/env_1*/src/openupgrade/openupgrade_scripts/scripts/*/*/upgrade_analysis_work.txt
}

oow_v() {
    cd src/env_${1}.0/src/;
}

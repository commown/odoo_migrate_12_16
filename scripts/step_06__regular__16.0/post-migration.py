from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

# Write custom script here

def new_ref(module, name, model, res_id, **kwargs):
    kwargs.update({"module": module, "name": name, "model": model, "res_id": res_id})
    return env["ir.model.data"].create(kwargs)

# mail.template helpers
def copy_t10n_to_t10n(obj_recordset, field, orig_lang, target_lang):
    for obj in obj_recordset:
        obj.with_context(lang=target_lang)[field] = obj.with_context(lang=orig_lang)[field]

def replace_str_in_field(obj_recordset, field, lang, origin_str, target_str):
    for obj in obj_recordset:
        obj.with_context(lang=lang)[field] = obj.with_context(lang=lang)[field].replace(origin_str, target_str)


# Ticket 39426
env.ref("website.default_website").update(
    {
        "recaptcha_v2_enabled": True,
        "recaptcha_v2_resp_attr": "h-captcha-response",
        "recaptcha_v2_html_class": "h-captcha",
        "recaptcha_v2_api_url": "https://js.hcaptcha.com/1/api.js",
        "recaptcha_v2_verify_url": "https://api.hcaptcha.com/siteverify",
    }
)
env.cr.execute(
    """UPDATE website
    SET recaptcha_v2_site_key = recaptcha_key_site,
    recaptcha_v2_secret_key = recaptcha_key_secret
    """
)


# Modules installation related to various tickets
module_names = [
    "account_analytic_tag", # Ticket 43648
    "account_move_line_reconcile_manual", # Ticket 44968
    "account_reconcile_oca",
]

for module in env['ir.module.module'].search([("name", "in", module_names)]):
    module.button_immediate_install()

# Ticket #40262
env.ref('website_sale.product_custom_text').active = False
env.ref("website_sale.product_share_buttons").active = False

# Ticket #43639
# => Remove orphenated views from 12.0 module crm_phone
env['ir.ui.view'].search([("name", "in", ["phonecall.res.partner.form", "crm_phone.crm_lead.form"])]).unlink()

# Ticket #43795
base_nps_tmpl = env.ref("project_rating_nps.nps_rating_request_email")
base_nps_tmpl.reset_template()

# Ticket #43785
dupl_nps_tmpl = env['mail.template'].search([("name", "like", "[Commown] NPS")])
dupl_nps_tmpl.write({
    "body_html": base_nps_tmpl.body_html,
    "partner_to": base_nps_tmpl.partner_to,
    "lang": base_nps_tmpl.lang,
})
copy_t10n_to_t10n(dupl_nps_tmpl, "body_html", "fr_FR", "de_DE")
copy_t10n_to_t10n(dupl_nps_tmpl, "body_html", "fr_FR", "en_US")

# Ticket #44730
label_group = env.ref("commown_shipping.group_print_label")
role_names = ["Logistique", "Support", "Gestion des contrats", "Commercial", "Admin Odoo", "Directoire"]

for role in env['res.users.role'].search([('name', 'in', role_names)]):
    role.implied_ids |= label_group

# Ticket #43988/#
b2b_chans = env["mail.channel"].search([("partner_companies", "!=", False)])
b2b_chans += env["mail.channel"].browse(289) # Assemblée Générale

# Remove current and ex employees from the mail.channel subscribers.
partners_domain = ["|", ("partner_id.user_ids.groups_id", "=", env.ref("base.group_user").id), ("partner_id.active", "=", False)]

env["mail.channel.member"].search([("channel_id", "in", b2b_chans.ids)] + partners_domain).unlink()
env["mail.followers"].search([("res_model", "=", "mail.channel"), ("res_id", "in", b2b_chans.ids)] + partners_domain).unlink()

# Creating new Support user, and subscribing them to all B2B channels.
with open("/env/scripts/step_06__regular__16.0/support_user.txt", "r") as f:
    password = f.read().strip('\n')

support_user = env["res.users"].create(
    {
        "name": "Support Commown",
        "login": "support_commown",
        "password": password,
        "website_id": env.ref("website_b2b.b2b_website").id,
        "role_line_ids": [
            (0, 0, {"role_id": env.ref("commown_user_roles.employee").id}),
            (0, 0, {"role_id": env.ref("commown_b2b_mail_channel.role_b2b_channels").id}),
        ],
        "notification_type": "inbox",
    }
)
support_user.partner_id.parent_id = env["res.partner"].search([("name", "=", "Commown")])

b2b_chans.add_members(partner_ids=support_user.partner_id.ids)

# Set B2B chans. auto-subscribe roles to new B2B channel role
env.ref("commown_b2b_mail_channel.roles_subscribed_to_support_chan").value = "commown_b2b_mail_channel.role_b2b_channels"

# Ticket #45262
env.ref("commown_user_roles.employee").implied_ids |= env.ref("base.group_allow_export")

# Ticket #45022
for cron in env['ir.cron'].search([("active", "in", (True, False)), ("model_name", "=", False)]):
    cron.model_name = cron.model_id.name

# Ticket #45263
# Recompute stored computed field rating_text, to avoid issues with rating_last_text field in rating.mixin (=> project.task)
openupgrade.logged_query(
    env.cr,
    """
        UPDATE rating_rating
        SET rating_text = CASE
            WHEN rating >= 9 THEN 'promoter'
            WHEN rating <= 6 THEN 'detractor'
            ELSE 'neutral'
        END;
    """,
)

# Ticket #44773
slimpay_apml = env['account.payment.method.line'].search([('code', '=', 'slimpay')])
slimpay_apml.payment_provider_id = env.ref("account_payment_slimpay.payment_provider_slimpay")

slimpay_journal = env['account.journal'].search([("name", "like", "Règlements % Slimpay")])
slimpay_journal.inbound_payment_method_line_ids |= slimpay_apml.filtered(lambda apml: apml.payment_type == "inbound")
slimpay_journal.outbound_payment_method_line_ids |= slimpay_apml.filtered(lambda apml: apml.payment_type == "outbound")

# Ticket #45766

# - This reference not exist any longer in v16 module:
env.ref("payment_slimpay_issue.smspro_payment_issue").unlink()

# Remove data from old module commown_payment_slimpay_issue:
# (note there are 2 references to the same data, all will be removed by this line)
env.ref("commown_payment_slimpay_issue.action_send_payment_issue_sms").unlink()

# General user created template modifications.
# - urban_mine templates
copy_t10n_to_t10n(env['mail.template'].browse(278), "body_html", "fr_FR", "en_US")
copy_t10n_to_t10n(env['mail.template'].browse(340), "body_html", "fr_FR", "en_US")

# - 'user_id' -> 'user_ids[0]'
replace_str_in_field(env['mail.template'].browse(406), "body_html", "en_US", "object.user_id", "object.user_ids and object.user_ids[0]")
replace_str_in_field(env['mail.template'].browse(406), "body_html", "de_DE", "object.user_id", "object.user_ids and object.user_ids[0]")

# Remove outdated mail templates linked to contract emails generators
outdated_tmpls_ids = [148, 173, 151, 184]
env['mail.template'].browse(outdated_tmpls_ids).exists().active = False

# Ticket #45098
with open("/env/scripts/step_06__regular__16.0/outdated_filter_ids.txt", "r") as f:
    # Remove filters deemed ununsed by our users
    outdated_filter_ids = list(map(int, f.read().split()))
    env["ir.filters"].browse(outdated_filter_ids).exists().unlink()

with open("/env/scripts/step_06__regular__16.0/v12_inactive_filter_ids.txt", "r") as f:
    # Filter out filters already inactive in v12
    v12_inactive_filter_ids = list(map(int, f.read().split()))

v16_ko_filters = env['ir.filters'].search([("active", "=", False), ("id", "not in", v12_inactive_filter_ids)])

def filter_replace_str(filters, model, origin_str, target_str):
    affected_filters = filters.filtered(lambda f: f.model_id == model and origin_str in f.domain)
    replace_str_in_field(affected_filters, "domain", "fr_FR", origin_str, target_str)

filter_replace_str(v16_ko_filters, "account.move", "dummy_account_id", "line_ids.account_id")
filter_replace_str(v16_ko_filters, "account.move", "reference", "payment_reference")
filter_replace_str(v16_ko_filters, "account.move", "tax_line_ids", "invoice_line_ids.tax_ids")
filter_replace_str(v16_ko_filters, "account.move", '("state", "=", "paid")', '("payment_state", "=", "paid")')
filter_replace_str(v16_ko_filters, "account.move", "'open'", '"posted"')
filter_replace_str(v16_ko_filters, "account.move", '"open"', '"posted"')

filter_replace_str(v16_ko_filters, "contract.contract", '"TODAY"', 'context_today().strftime("%Y-%m-%d")')
filter_replace_str(v16_ko_filters, "contract.contract", "'TODAY'", 'context_today().strftime("%Y-%m-%d")')

filter_replace_str(v16_ko_filters, "crm.lead", '"TODAY"', 'context_today().strftime("%Y-%m-%d")')

filter_replace_str(v16_ko_filters, "project.task", "user_id", "user_ids")

filter_replace_str(v16_ko_filters, "res.partner", "customer", "customer_rank")
filter_replace_str(v16_ko_filters, "res.users", "customer", "customer_rank")

v16_ko_filters.active = True

# Assign new actions to filters with outdated actions
action_equivalences = {
    210: "account.action_move_out_invoice_type",
    1053: "account.action_move_in_invoice_type",
    173: "account.action_account_moves_all",
    362: "crm.crm_lead_action_pipeline",
    363: "crm.crm_lead_action_my_activities",
    399: "mass_mailing.mailing_mailing_action_mail",
    133: False, # "sales_team.crm_team_action_pipeline" / "sales_team.crm_team_action_sales"
    699: "stock.dashboard_open_quants",
    701: False, # "stock.action_change_product_quantity" / a custom action in action_open_quants
    1063: "account_asset_management.action_account_asset_report",
}

for outdated_action_id, new_action_xml_id in action_equivalences.items():
    if new_action_xml_id:
        new_action = env.ref(new_action_xml_id).id
    else:
        new_action = False

    env["ir.filters"].search([("action_id", "=", outdated_action_id)]).action_id = new_action

# Ticket #46100
# Re-add after-sale tags to stage names, and reset the timed automated actions.
env.ref("commown_support.stage_pending").with_context(lang="en_US").name += " [after-sale: pending]"
env.ref("commown_support.stage_long_term_followup").with_context(lang="en_US").name += " [after-sale: manual]"

env["base.automation"].search([("action_server_id", "=", env.ref("commown_support.action_move_issue_to_stop_waiting_stage").id)]).last_run = False

# Ticket #45680
ctm_rule = env.ref("customer_team_manager.res_partner_customer_user_rule")
ctm_rule.domain_force = ctm_rule.domain_force.replace("'id', 'child_of'", "'parent_id', '='")

# Ticket #44958
kpi_migration = {
    "commown_expenses": {"weight": 2},
    "commown_turnover": {"weight": 1},
    "commown_turnover_cumulated": {"weight": 2},
    "commown_customer_fidelity": {"weight": 2}
}
sql_views = env["bi.sql.view"].search([]).sorted(lambda v: kpi_migration.get(v.technical_name, {}).get("weight", 0), reverse=True)

env.cr.execute("SELECT matviewname FROM pg_matviews")
sql_mat_views = set(l[0] for l in env.cr.fetchall())

for sql_view in sql_views:
    # Build new KPI SQL create values
    with open(f"/env/odoo-commown-kpi-sql-views/{sql_view.technical_name}.sql", "r") as f:
        query = f.read()

    # Drop materialized view/table
    view_name = f"x_bi_sql_view_{sql_view.technical_name}"
    if view_name in sql_mat_views:
        env.cr.execute("DROP MATERIALIZED VIEW IF EXISTS %s" % view_name)
    else:
        env.cr.execute("DROP TABLE IF EXISTS %s" % view_name)

    # Set view back to draft
    sql_view.button_reset_to_model_valid()
    sql_view.button_reset_to_sql_valid()
    sql_view.button_set_draft()

    # Set new query / reset query
    sql_view.query = query
    sql_view.button_validate_sql_expression()

    # Setup new field
    if sql_view.technical_name == "commown_order_by_product":
        sql_view.bi_sql_view_field_ids.filtered(lambda f: f.name == "x_market").write({
            "field_description": "Marché",
            "graph_type": "col",
            "is_index": True,
            "is_group_by": True,
        })

    sql_view.button_create_sql_view_and_model()
    sql_view.flush_recordset()
    sql_view.button_create_ui()

# Ticket #44777
env["account.statement.import.sheet.mapping"].search([("name", "=", "Crédit Coopératif")]).write(
    {
        "header_lines_skip_count": 5,
        "footer_lines_skip_count": 1,
        "amount_type": "distinct_credit_debit",
        "amount_debit_column": "Débit",
        "amount_credit_column": "Crédit",
        "amount_inverse_sign": True,
    }
)

env["account.statement.import.sheet.mapping"].search([("name", "=", "La Nef")]).write(
    {
        "amount_type": "distinct_credit_debit",
        "amount_debit_column": "Débit",
        "amount_credit_column": "Crédit",
        "amount_inverse_sign": True,
        "description_column": "Libellé de la dépense",
        "notes_column": "Type de dépense",
        "reference_column": False,
    }
)

env.cr.commit()

# Uninstall unported modules
unported_modules = env['ir.module.module'].search([('name', 'in', ['account_invoice_view_payment', 'commown_lineageos', 'crm_phone', 'mass_operation_abstract'])])
unported_modules.button_immediate_uninstall()

import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

# Write custom script here

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


# Ticket #43648
env['ir.module.module'].search([("name", "=", "account_analytic_tag")]).button_immediate_install()

# Ticket #40262
env.ref('website_sale.product_custom_text').active = False
env.ref("website_sale.product_share_buttons").active = False

# Ticket #43639
# => Remove orphenated views from 12.0 module crm_phone
env['ir.ui.view'].search([("name", "in", ["phonecall.res.partner.form", "crm_phone.crm_lead.form"])]).unlink()

# Ticket #43785
duplicated_nps_tmpl = env['mail.template'].search([("name", "like", "[Commown] NPS")])
affected_stages = env['project.task.type'].search([("mail_template_id", "=", duplicated_nps_tmpl.id)])

affected_stages.mail_template_id = base_nps_template = env.ref("project_rating_nps.nps_rating_request_email")
duplicated_nps_tmpl.unlink()

# Ticket #44730
label_group = env.ref("commown_shipping.group_print_label")
role_names = ["Logistique", "Support", "Gestion des contrats", "Commercial", "Admin Odoo", "Directoire"]

env["res.users.role"].search([("name", "in", role_names)]).implied_ids |= label_group

env.cr.commit()

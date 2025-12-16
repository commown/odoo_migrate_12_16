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

# Ticket #44730
label_group = env.ref("commown_shipping.group_print_label")
role_names = ["Logistique", "Support", "Gestion des contrats", "Commercial", "Admin Odoo", "Directoire"]

for role in env['res.users.role'].search([('name', 'in', role_names)]):
    role.implied_ids |= label_group

# Ticket #43988/#
env["mail.channel"].browse(289).active = False # Assemblée Générale
b2b_chans = env["mail.channel"].search([("partner_companies", "!=", False)])

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
        "role_line_ids": [(0, 0, {"role_id": env.ref("commown_user_roles.employee").id})],
    }
)
support_user.partner_id.parent_id = env["res.partner"].search([("name", "=", "Commown")])

b2b_chans.add_members(partner_ids=support_user.partner_id.ids)

# Ticket #45262
env.ref("commown_user_roles.employee").implied_ids |= env.ref("base.group_allow_export")

# Ticket #45022
for cron in env['ir.cron'].search([("active", "in", (True, False)), ("model_name", "=", False)]):
    cron.model_name = cron.model_id.name

# Ticket #45263
# Recompute stored computed field rating_text, to avoid issues with rating_last_text field in rating.mixin (=> project.task)
env['rating.rating'].search([])._compute_rating_text()


env.cr.commit()

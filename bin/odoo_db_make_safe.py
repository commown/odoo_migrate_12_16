import os.path as osp

# Remove directoire chan messages:
print("Removing messages...")
env["mail.message"].search([("channel_ids", "ilike", "directoire")]).unlink()
env["mail.message"].search([("channel_ids", "ilike", "RH")]).unlink()
env.cr.commit()
print(" Done!")

# Unlink existing mail servers:
for mail_server in env['ir.mail_server'].search([]):
    print("Deleting smtp mail server %s..." % mail_server.name.encode('utf-8'))
    mail_server.unlink()
env.cr.commit()
print(" Done!")

# Deactivate all crontabs:
print("Deactivating all crontabs...")
env['ir.cron'].search([]).update({'active': False})
env.cr.commit()
print(" Done!")

# Remove fetch mail servers
print("Removing fetching mail servers...")
for server in env['fetchmail.server'].search([]):
    print("Deleting fetch mail server %s..." % server.name.encode('utf-8'))
    server.unlink()
env.cr.commit()
print(" Done!")

# Create debugging local imap server:
print("Creating debugging local imap server...")
env['fetchmail.server'].create({
    'name': 'mail-devel',
    'state': 'done',
    'object_id': env.ref('project.model_project_task').id,
    })
env.cr.commit()
print(" Done!")

# Create debugging local mail server:
print("Creating debug mail server...")
env['ir.mail_server'].create({
    'name': 'mail-devel',
    'smtp_debug': True,
    })
env.cr.commit()
print(" Done!")

# Set base-url
env['ir.config_parameter'].set_param(
    'web.base.url', 'https://odoo-16.commown.priv',
)
env.cr.commit()

# Set websites' domain
website_domains = {
    1: "https://odoo-v16.commown.priv",
    2: "https://pro-v16.commown.priv",
}
for website_id, domain in website_domains.items():
    website = env["website"].browse(int(website_id))
    print(
        "Changing domain of '%s' website from '%s' to '%s'"
        % (website.name, website.domain, domain)
    )
    website.domain = domain
env.cr.commit()

# Deactivate cooperative WS
self.env['ir.config_parameter'].set_param(
  'commown_cooperative_campaign.base_url', 'deactivated')
env.cr.commit()

# Create new mandates on Slimpay sandbox
if osp.isfile('/tmp/mandates.json') and env['ir.module.module'].search([('name', '=', 'payment_slimpay_dump_restore_utils')]):
    env['payment.provider']._slimpay_restore_mandates()
else:
    print("!!! WARNING !!! Module payment_slimpay_dump_restore_utils not avail")
env.cr.commit()

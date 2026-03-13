import os.path as osp

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

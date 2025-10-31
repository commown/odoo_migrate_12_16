import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

# Write custom script here

# Ticket #43639
env['ir.module.module'].search([("name", "=", "crm_phone")]).button_immediate_uninstall()

env.cr.commit()

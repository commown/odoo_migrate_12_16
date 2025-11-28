import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

# Ticket #44870
# -> Install this module now to trigger its v16 post-migration script
env["ir.module.module"].search([("name", "=", "web_chatter_position")]).button_immediate_install()

env.cr.commit()

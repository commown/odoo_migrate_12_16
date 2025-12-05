import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

# Ticket #44870
# -> Install this module now to trigger its v16 post-migration script
env["ir.module.module"].search([("name", "=", "web_chatter_position")]).button_immediate_install()

# Ticket #44773
# Re-execute end-migration account request, to assign newly created payment method lines to older account.payment records
env.cr.execute(
    """
    UPDATE account_payment ap
    SET payment_method_line_id = apml.id
    FROM account_move am
    JOIN account_payment_method_line apml ON apml.journal_id = am.journal_id
    WHERE ap.move_id = am.id AND ap.payment_method_id = apml.payment_method_id
    """
)

env.cr.commit()

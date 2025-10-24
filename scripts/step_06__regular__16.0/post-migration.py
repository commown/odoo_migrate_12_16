import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

# Write custom script here

slimpay_tech_name = ""
env.ref("account_payment_slimpay.payment_provider_slimpay").tech_name = "payment_provider_slimpay"

colissimo 

env.cr.commit()

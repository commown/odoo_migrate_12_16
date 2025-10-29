import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

# Write custom script here

# cf. PR 481: Assign tech_name to noupdate records

env.ref("account_payment_slimpay.payment_provider_slimpay").tech_name = "payment_provider_slimpay"
env.ref("colissimo_shipping.shipping-account-colissimo-std-account").tech_name = "shipping-account-colissimo-std-account"
env.ref("colissimo_shipping.shipping-account-colissimo-support-account").tech_name = "shipping-account-colissimo-support-account"

env.cr.commit()

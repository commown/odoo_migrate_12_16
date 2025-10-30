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


# cf. PR 481: Assign tech_name to noupdate records

env.ref("account_payment_slimpay.payment_provider_slimpay").tech_name = "payment_provider_slimpay"
env.ref("colissimo_shipping.shipping-account-colissimo-std-account").tech_name = "shipping-account-colissimo-std-account"
env.ref("colissimo_shipping.shipping-account-colissimo-support-account").tech_name = "shipping-account-colissimo-support-account"

env.cr.commit()

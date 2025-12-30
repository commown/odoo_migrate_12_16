import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

# Ticket #45856
with open("/env/bin/mt-smspro_payment_issue-body_current.txt", "w") as f:
  f.write(env.ref("payment_slimpay_issue.smspro_payment_issue").body_html)

env.cr.commit()

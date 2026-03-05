from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

# Ticket #44489
for pt in env['product.template'].search([("website_description", "!=", False)]):
  for lang in ("fr_FR", "de_DE", "en_US"):
    with open(f"/env/pt_{pt.id}_{lang}.txt", "w") as f:
      f.write(pt.with_context(lang=lang).website_description)

# Ticket #45719
env.ref("sales_team.salesteam_website_sales").use_opportunities = True

# Ticket #48394
openupgrade.logged_query(
  env.cr,
  """
  UPDATE account_move_line aml
  SET account_root_id = aa.root_id
  FROM account_account aa
  WHERE aml.account_root_id IS NULL AND aa.id = aml.account_id
  """
)

env.cr.commit()

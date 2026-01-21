import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

# Ticket #44489
pts = env['product.template'].search([("website_description", "!=", False)])
for pt in pts:
  for lang in ("fr_FR", "de_DE", "en_US"):
    with open(f"/env/pt_{pt.id}_{lang}.txt", "r") as f:
      pt.with_context(lang=lang).website_description = f.read()

env['ir.translation'].search(
  [
    ("res_id", "in", pts.ids),
    ('name', '=', 'product.template,website_description'),
    ("state", "=", "to_translate"),
  ]
).state = "translated"

# Ticket #45090
env["account.bank.statement.line"]._compute_is_reconciled()

env.cr.commit()

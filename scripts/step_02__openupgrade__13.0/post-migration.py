import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

# Ticket #44489
for pt in env['product.template'].search([("website_description", "!=", False)]):
  for lang in ("fr_FR", "de_DE", "en_US"):
    with open(f"/env/pt_{pt.id}_{lang}.txt", "w") as f:
      f.write(pt.with_context(lang=lang).website_description)

env.cr.commit()

import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

# Ticket #47933
# Setting this view's priority low, so that after the next update,
# it doesn't take priority over other views.
env.ref("website_livechat.im_livechat_channel_view_form_add").priority = 99

env.cr.commit()

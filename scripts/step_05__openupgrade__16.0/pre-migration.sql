-- Ticket #43655
UPDATE ir_model_data SET module="account_payment_slimpay", name="payment_provider_slimpay"
WHERE module="payment" AND name="payment_acquirer_slimpay";

-- Ticket #42292
UPDATE ir_model_data SET module='customer_manager_base'
WHERE module='customer_team_manager' AND name='group_customer_admin';

-- Ticket #40613
UPDATE ir_model_data SET module='commown_investment_sale'
WHERE module='commown' AND name='investment_payment_term';

UPDATE ir_model_data SET module='commown_investment_sale'
WHERE module='commown' AND name='investment_followup_project';

UPDATE ir_model_data SET module='commown_investment_sale'
WHERE module='commown' AND name='investment_followup_start_stage';

-- Ticket #40616
UPDATE ir_model_data SET module='commown_support'
WHERE module='commown' AND NAME= 'mail_template_issue_reminder';

UPDATE ir_model_data SET module='commown_support'
WHERE module='commown' AND NAME= 'sms_template_issue_reminder';

UPDATE ir_model_data SET module='commown_support'
WHERE module='commown_self_troubleshooting' AND NAME= 'support_project';

UPDATE ir_model_data SET module='commown_support'
WHERE module='commown_self_troubleshooting' AND NAME= 'commercial_project';

UPDATE ir_model_data SET module='commown_support'
WHERE module='commown_self_troubleshooting' AND NAME= 'stage_callback';

UPDATE ir_model_data SET module='commown_support'
WHERE module='commown_self_troubleshooting' AND NAME= 'stage_pending';

UPDATE ir_model_data SET module='commown_support'
WHERE module='commown_self_troubleshooting' AND NAME= 'stage_received';

UPDATE ir_model_data SET module='commown_support'
WHERE module='commown_self_troubleshooting' AND NAME= 'stage_solved';

UPDATE ir_model_data SET module='commown_support'
WHERE module='commown_self_troubleshooting' AND NAME= 'stage_long_term_followup';

-- Ticket #40659
UPDATE ir_model_data SET module='website_b2b'
WHERE module='website_sale_b2b' AND NAME= 'b2b_website';

-- Ticket #40659
DELETE from ir_model_data
WHERE module='commown' and name='mass_reconcile';

DELETE from ir_model_data
WHERE module='commown' and name='reconcile_method_simple_partner_custom';

-- Ticket #40337
DELETE from ir_actions WHERE id=460;

delete from ir_ui_view where name='commown_automated_control.base_automation';
delete from ir_ui_view where name='crm.phone.preferences.option.view';
delete from ir_ui_view where name='crm.phone.res.users.form';

-- Ticket 39426
UPDATE website
SET recaptcha_v2_site_key = recaptcha_key_site, recaptcha_v2_secret_key = recaptcha_key_secret;

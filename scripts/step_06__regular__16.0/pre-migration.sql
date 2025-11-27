delete from ir_ui_view where name='commown_automated_control.base_automation';
delete from ir_ui_view where name='crm.phone.preferences.option.view';
delete from ir_ui_view where name='crm.phone.res.users.form';

-- Ticket #43988/#
-- Written by Florent Cayre
update mail_channel C set channel_type='channel' 
where exists(
    select 1 from res_partner P where P.mail_channel_id = C.id
);

-- Ticket #43657/#
update payment_provider set tech_name = 'slimpay' where id = 11; -- account_payment_slimpay.payment_provider_slimpay
update commown_shipping_account set tech_name = 'shipping-account-colissimo-std-account'
where id = 1; -- commown_shipping.shipping-account-colissimo-std-account
update commown_shipping_account set tech_name = 'shipping-account-colissimo-support-account'
where id = 2; -- commown_shipping.shipping-account-colissimo-support-account


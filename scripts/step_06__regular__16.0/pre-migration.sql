delete from ir_ui_view where name='commown_automated_control.base_automation';
delete from ir_ui_view where name='crm.phone.preferences.option.view';
delete from ir_ui_view where name='crm.phone.res.users.form';

-- Ticket #43988/#
-- Written by Florent Cayre
update mail_channel C set channel_type='channel' 
where exists(
    select 1 from res_partner P where P.mail_channel_id = C.id
);
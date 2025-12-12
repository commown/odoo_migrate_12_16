-- Ticket #44773/#
update account_payment_method
set
    code = 'slimpay',
    name = 'Slimpay (' || payment_type || ')'
where code = 'electronic';


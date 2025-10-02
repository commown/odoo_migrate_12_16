-- Add a inbound payment method for journal "Règlements Fournisseurs -
-- Paypal" because there are test account payment (IDS: 2352, 2355,
-- 2357, 2356, 2358, 2360, 2362, 2359, 2361, 2365, 2364, 2363) that
-- are inbound but the journal does not support it.

-- We cannot simply remove these payments because their number are
-- supposed to be continuous.

INSERT INTO account_journal_inbound_payment_method_rel
VALUES (11, 1)
ON CONFLICT DO NOTHING;

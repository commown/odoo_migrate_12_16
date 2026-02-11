import datetime


# Fetch affected moves (inaccurate name and associated to an asset) and their journals
env.cr.execute(
    """
    SELECT  
        am.id, aj.id
    FROM
        account_move am
        JOIN account_journal aj ON am.journal_id = aj.id
    WHERE
        am.move_type = 'entry' AND
        am.company_id = %(company_id)s AND
        am.date >= %(fiscal_year_start)s AND
        am.state = 'posted' AND
        am.name NOT LIKE aj.code || '/%%' AND
        EXISTS (
            SELECT *
            FROM account_asset_line aal
            WHERE
                aal.move_id = am.id
        )
    """,
    {
        "company_id": env.company.id,
        "fiscal_year_start": env.company.fiscal_year_date_from.strftime("%Y-%m-%d"),
    },
)
res = env.cr.fetchall()
affected_moves_ids = ids = [row[0] for row in res]
journal_ids = {row[1] for row in res}

# Main code
for journal_id in journal_ids:
    journal = env["account.journal"].browse(journal_id)
    dom_journal_moves = [
        ("id", "in", affected_moves_ids),
        ("journal_id", "=", journal_id),
    ]

    valid_mv = env["account.move"].search(
        [("journal_id", "=", journal_id), ("name", "ilike", f"{journal.code}/%")],
        order="sequence_number desc",
        limit=1,
    )
    reset = valid_mv._deduce_sequence_number_reset(valid_mv.name)

    if reset in ("month", "year"):
        groupby = env["account.move"].read_group(
            dom_journal_moves, ["date"], [f"date:{reset}"]
        )

        for group in groupby:
            time_range_start = datetime.datetime.strptime(
                group["__range"][f"date:{reset}"]["from"], "%Y-%m-%d"
            )

            prefix = f"{journal.code}/{time_range_start.year}/"
            if reset == "month":
                prefix += f"{time_range_start.month:02d}/"

            valid_mv = env["account.move"].search(
                [("sequence_prefix", "=", prefix), ("journal_id", "=", journal_id)],
                order="sequence_number desc",
                limit=1,
            )
            if valid_mv:
                # Already existing sequence
                last_sequence = valid_mv.name
            else:
                # New sequence init. (based on account.move _get_starting_sequence)
                last_sequence = prefix + ("0000" if reset == "month" else "00000")

            format, format_values = valid_mv._get_sequence_format_param(last_sequence)

            date_range_moves = env["account.move"].search(
                group["__domain"], order="id asc"
            )

            for move in date_range_moves:
                format_values["seq"] += 1
                move.name = format.format(**format_values)

    elif reset == "never":
        # NOT CHECKED - DOESN'T APPLY TO OUR DATABASE
        journal_moves = env["account.move"].search(dom_journal_moves, order="id asc")
        format, format_values = valid_mv._get_sequence_format_param(valid_mv.name)

        for move in journal_moves:
            format_values["seq"] += 1
            move.name = format.format(**format_values)

    elif reset == "year_range":
        date_from, date_to = valid_mv._get_sequence_year_range()
        # TODO
        pass

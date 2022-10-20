import sqlite3
import string
from gnuCashLib.data_objects import Account, Transaction


def sql_get_accounts():
    return """
            select      acc.guid, acc.name, acc.account_type, acc.description
            from        accounts  acc
            inner join  accounts  p   on p.guid = acc.parent_guid
                                      and p.parent_guid is null
                                      and p.account_type = 'ROOT'
                                      and p.name = 'Root Account'
            where acc.account_type in ('ASSET', 'CREDIT', 'BANK', 'LIABILITY')
    """


def sql_get_categories():
    return """
            select      a.guid, a.name, a.account_type, a.description
            from        accounts a
            where       a.account_type in ('EXPENSE', 'INCOME')
    """


def sqlite_account_export(data_source: string) -> dict[string, Account]:
    sql = f"""
            {sql_get_accounts()}
            union
            {sql_get_categories()}
        """

    accounts: dict[string, Account] = {}

    con = sqlite3.connect(data_source)
    cur = con.cursor()
    for row in cur.execute(sql):
        account = Account(row)
        accounts[account.guid] = account

    con.close()

    return accounts


def sqlite_transaction_export(data_source: string, accounts: dict[string, Account]) -> dict[string, Transaction]:
    sql = f"""
            with cteAccounts(guid, name, account_type, description) AS
            (
                {sql_get_accounts()}
                union
                {sql_get_categories()}
            )
            select
                            t.guid              as TrxGuid,
                            acc.guid            as AccGuid,
                            acc.name            as AccountName,
                            t.post_date         as DatePosted,
                            t.Num               as Ref,
                            t.Description,
                            sl.string_val       as Notes,
                            s.reconcile_state   as isReconciled,
                            case acc.account_type
                                when 'EQUITY' then ROUND((s.value_num / -100.0), 2)
                                else ROUND((s.value_num / 100.0), 2)
                            end as trxValue
            from            splits        as s
            inner join      transactions  as t    on t.guid = s.tx_guid
            left outer join cteAccounts   as acc  on acc.guid = s.account_guid
            left outer join slots         as sl   on sl.obj_guid = t.guid and sl.name = 'notes'
            order by        t.guid,
                            t.post_date asc
    """

    transactions: dict[string, Transaction] = {}

    con = sqlite3.connect(data_source)
    cur = con.cursor()
    for row in cur.execute(sql):
        trx = Transaction(row, accounts)

        if trx.transaction_guid in transactions:
            # Merge current transaction with the existing one. Since this is double entry bookkeeping
            # there is usually one account entry and one (or could be more) category entry
            existing_trx = transactions[trx.transaction_guid]

            if trx.is_account_side:
                # Record the account rather than category details on the transaction
                existing_trx.account_guid = trx.account_guid
                existing_trx.account_name = trx.account_name

            if len(trx.account_splits) > 0:
                # Should always be one split per transaction unless added here
                existing_trx.account_splits.extend(trx.account_splits)

            if len(existing_trx.account_splits) > 2:
                print(f"WARNING: Multiple splits for {existing_trx}, but only two splits currently supported!")

            # Update the accounts reference with the existing_trx
            for acc_key, acc in accounts.items():
                if existing_trx.transaction_guid in acc.transactions:
                    acc.transactions[existing_trx.transaction_guid] = existing_trx

        else:
            transactions[trx.transaction_guid] = trx

    con.close()

    return transactions

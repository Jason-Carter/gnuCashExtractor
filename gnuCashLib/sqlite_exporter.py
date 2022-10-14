import sqlite3
import string
from gnuCashLib.data_objects import Account, Transaction


def sqlite_account_export(data_source: string) -> dict[string, Account]:
    sql = """
            with recursive cteAccounts(guid, name, account_type, parent_guid, code, 
                                        description, hidden, placeholder, level, path) AS
            (
                select guid, name, account_type, parent_guid, code,
                        description, hidden, placeholder, 0, ''
                from accounts
                where parent_guid is null
                and name = 'Root Account'
                union all
                select a.guid, a.name, a.account_type, a.parent_guid, a.code,
                            a.description, a.hidden, a.placeholder, p.level + 1, p.path || ':' || a.name
                from        accounts a
                inner join  cteAccounts p on p.guid = a.parent_guid
                order by 9 desc -- by using desc we're doing a depth-first search
            )
            select substr('                                        ', 1, level* 10) || name 'hierarchy',
                    name,
                    guid,
                    description,
                    substr(path, 2, length(path)) 'path',
                    account_type, level
            from    cteAccounts
            where account_type in ('ASSET', 'CREDIT', 'BANK', 'EXPENSE', 'INCOME', 'LIABILITY')
        """

    accounts: dict[string, Account] = {}  # list()  # List[Account]()

    con = sqlite3.connect(data_source)
    cur = con.cursor()
    for row in cur.execute(sql):
        account = Account(row)
        accounts[account.guid] = account

    con.close()

    return accounts


def sqlite_transaction_export(data_source: string, accounts: dict[string, Account]) -> dict[string, Transaction]:
    sql = """
            with recursive cteCategories(guid, name, account_type, parent_guid, code,
                                        description, hidden, placeholder, level, path) AS
            (
                select  guid, name, account_type, parent_guid, code,
                        description, hidden, placeholder, 0, ''
                from    accounts 
                where   parent_guid is null
                and     name = 'Root Account'
                union all
                select      a.guid, a.name, a.account_type, a.parent_guid, a.code,
                            a.description, a.hidden, a.placeholder, p.level + 1, p.path || ':' || a.name
                from        accounts a
                inner join  cteCategories p on p.guid = a.parent_guid
                where       a.account_type in ('EXPENSE', 'INCOME')
                order by 9 desc -- by using desc we're doing a depth-first search
            ),
            cteAccounts(guid, name, account_type, description) as
            (
                select      acc.guid, acc.name, acc.account_type, acc.description
                from        accounts  acc
                inner join  accounts  p   on p.guid = acc.parent_guid
                                          and p.parent_guid is null
                                          and p.account_type = 'ROOT'
                                          and p.name = 'Root Account'
                where acc.account_type in ('ASSET', 'CREDIT', 'BANK', 'LIABILITY')
            )
            select
                            t.guid              as TrxGuid,
                            acc.guid            as AccGuid,
                            acc.name            as AccountName,
                            t.post_date         as DatePosted,
                            t.Num               as Ref,
                            t.Description,
                            sl.string_val       as Notes,
                            cat.guid            as CategoryGuid,
                            cat.name            as Transfer,
                            s.reconcile_state   as isReconciled,
                            case acc.account_type
                                when 'EQUITY' then ROUND((s.value_num / -100.0), 2)
                                else ROUND((s.value_num / 100.0), 2)
                            end as trxValue
            from            splits        as s
            inner join      transactions  as t    on t.guid = s.tx_guid
            left outer join cteAccounts   as acc  on acc.guid = s.account_guid
            left outer join cteCategories as cat  on cat.guid = s.account_guid
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
            existing_trx = transactions[trx.transaction_guid]
            # TODO: Update any attributes on trx that are not on existing_trx
            # TODO: Create a new method on Transaction to add missing attributes / splits (add_new_trx_values)
            existing_trx.account_splits.append(trx.account_splits)
        else:
            transactions[trx.transaction_guid] = trx

    con.close()

    return transactions

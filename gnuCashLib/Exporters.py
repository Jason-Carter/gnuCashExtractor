import sqlite3
import string
from typing import List
from gnuCashLib.DataObjects import Account, Transaction


class Exporter:
    def extract(self, data_source: string):
        pass


class SqliteAccountExporter(Exporter):
    sql = """
            with recursive cteAccounts(guid, name, account_type, parent_guid, code, description, hidden, placeholder, level, path) AS
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

    def extract(self, data_source: string) -> List[Account]:
        accounts = list()  # List[Account]()

        con = sqlite3.connect(data_source)
        cur = con.cursor()
        for row in cur.execute(self.sql):
            account = Account(row)
            accounts.append(account)

        con.close()

        return accounts


class SqliteTransactionExporter(Exporter):

    sql = """
            with recursive cteCategories(guid, name, account_type, parent_guid, code, description, hidden, placeholder, level, path) AS
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
    def extract(self, data_source: string) -> list[Transaction]:
        print("sql lite trx to do")


# class XmlExporter(Exporter):
#     def extract(self, data_source: string) -> List[Exporter]:
#         pass


def extract_data(data_source: string) -> list[Account]:
    """
    Extracts the Accounts and Transactions from the sqlite data source.

    :param data_source: full path to an sqlite3 database
    :return: a list of accounts with associated transactions from the sqlite3 database passed in the data_source
    """
    # Current assumption is data_source is an sqlLite db (xml support is for the future)

    print(f'Extracting accounts...')
    sql_acc_export = SqliteAccountExporter()
    acc_list = sql_acc_export.extract(data_source)
    print(f'{len(acc_list)} accounts extracted')

    print(f'Extracting transactions for each account...')

    return acc_list

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
            account = Account()
            account.set_account_from_db(row)
            accounts.append(account)

        con.close()

        return accounts


class SqliteTransactionExporter(Exporter):
    def extract(self, data_source: string) -> List[Transaction]:
        print("sql lite trx to do")


# class XmlExporter(Exporter):
#     def extract(self, data_source: string) -> List[Exporter]:
#         pass


def extract_data(data_source: string) -> None:
    """
    Extracts the Accounts and Transactions from the sqlite data source.

    :param data_source:
    :return:
    """
    # Current assumption is data_source is an sqlLite db (xml support is for the future)

    print('Extracting data from ' + data_source)

    print('Accounts...')
    sql_acc_export = SqliteAccountExporter()
    acc_list = sql_acc_export.extract(data_source)

    for acc in acc_list:
        print(acc)

    # print('Transactions for each account...')

    return

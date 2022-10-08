import string
from typing import List
from gnuCashLib.data_objects import Account
from gnuCashLib.sqlite_exporter import sqlite_account_export, sqlite_transaction_export


def extract_data(data_source: string) -> list[Account]:
    """
    Extracts the Accounts and Transactions from the sqlite data source.

    :param data_source: full path to an sqlite3 database
    :return: a list of accounts with associated transactions from the sqlite3 database passed in the data_source
    """
    # Current assumption is data_source is an sqlLite db (xml support is for the future)

    print(f'Extracting accounts...')
    acc_list = sqlite_account_export(data_source)
    print(f'{len(acc_list)} accounts extracted')

    print(f'Extracting transactions for each account...')
    sqlite_transaction_export(data_source, acc_list)

    return acc_list

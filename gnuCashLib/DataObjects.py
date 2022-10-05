import string
from datetime import datetime
from typing import List


class Account:
    def __init__(self):
        self.guid = ""
        self.name = ""
        self.description = ""
        self.account_type = ""
        self.hierarchy = ""
        self.hierarchy_level = 0
        self.transactions = List[Transaction]

    def __str__(self) -> string:
        return f'{self.account_type} / {self.name}'

    def set_account_from_db(self, row: tuple):
        """
            Example row for an account would be as follows:
                ('                    Council Tax',         # hierarchy
                'Council Tax',                              # name
                '2a23aa2ab98bdf746eca456c497ff1ff',         # guid
                '',                                         # description
                'Tax:Council Tax',                          # path
                'EXPENSE',                                  # account_type
                2)                                          # level

        :param row:
        :return:
        """
        self.hierarchy = row[0]
        self.name = row[1]
        self.guid = row[2]
        self.description = row[3]
        # row[4] path not currently used
        self.account_type = row[5]
        self.hierarchy_level = row[6]


class AccountSplit:
    def __init__(self):
        self.account = List[Account]
        self.reconciled = ""
        self.trx_value = 0

    def __str__(self) -> string:
        return f'{self.account} / {self.trx_value}'


class Transaction:
    #date_posted: datetime.datetime

    def __init__(self):
        self.transaction_guid = ""
        self.ref = ""
        self.description = ""
        self.memo = ""
        self.account_splits = List[AccountSplit]
        self.parent_accounts = List[Account]

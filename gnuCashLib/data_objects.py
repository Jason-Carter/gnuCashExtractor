import string
from datetime import datetime
from typing import List


class Account:
    def __init__(self, row: tuple):
        # Example row(tuple) for an account would be as follows:
        #
        #     ('                    Council Tax',       # hierarchy (includes leading spaces based on level)
        #      'Council Tax',                           # name
        #      '2a23aa2ab98bdf746eca456c497ff1ff',      # guid
        #      '',                                      # description
        #      'Tax:Council Tax',                       # path
        #      'EXPENSE',                               # account_type
        #      2)                                       # level

        # not interested in the path at the moment, so just ignore it
        self.hierarchy, self.name, self.guid, self.description, _, self.account_type, self.hierarchy_level = row

    def __str__(self) -> string:
        return f'{self.account_type} / {self.name}'

    @property
    def is_account(self) -> bool:
        match self.account_type.upper():
            case "ASSET" | "CREDIT" | "BANK":
                return True
            case _:
                return False

    @property
    def is_category(self) -> bool:
        match self.account_type.upper():
            case "EXPENSE" | "INCOME":
                return True
            case _:
                return False


class AccountSplit:
    def __init__(self):
        self.account = List[Account]
        self.reconciled = ""
        self.trx_value = 0

    def __str__(self) -> string:
        return f'{self.account} / {self.trx_value}'


class Transaction:
    # date_posted: datetime.datetime

    def __init__(self):
        self.transaction_guid = ""
        self.ref = ""
        self.description = ""
        self.memo = ""
        self.account_splits = List[AccountSplit]
        self.parent_accounts = List[Account]

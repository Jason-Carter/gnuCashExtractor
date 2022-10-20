import string


class Account:
    def __init__(self, row: tuple):
        # Example row(tuple) for an account would be as follows:
        #
        #     ('2a23aa2ab98bdf746eca456c497ff1ff',      # guid
        #      'Council Tax',                           # name
        #      'EXPENSE',                               # account_type
        #      '')                                      # description

        (self.guid, self.name, self.account_type, self.description) = row
        self.transactions = dict()

    def __str__(self) -> string:
        return f'{self.name} / {self.account_type} / {len(self.transactions)} transactions'

    @property
    def is_account(self) -> bool:
        return self.account_type.upper() in ["ASSET", "CREDIT", "BANK"]

    @property
    def is_category(self) -> bool:
        return self.account_type.upper() in ["EXPENSE", "INCOME"]


class AccountSplit:
    def __init__(self, account: Account, is_reconciled: bool, trx_value: float):
        self.account = account
        self.is_reconciled = is_reconciled
        self.trx_value = trx_value

    def __str__(self) -> string:
        return f'{self.account} / {self.trx_value}'


class Transaction:
    # date_posted: datetime.datetime

    def __init__(self, row: tuple, accounts: dict[string, Account]):
        # Example row(tuple) for a transaction for a category would be as follows:
        #
        # ('fff5f3783282da1b8df557655c3ed4ed',      # TrxGuid
        #  '0561c5ddbf424ab5ef86f6a98f6d5b03',      # AccGuid
        #  'DVDs',                                  # AccountName
        #  '2016-12-21 10:59:00',                   # DatePosted
        #  '',                                      # Ref
        #  'WH Smiths',                             # Description
        #  'Ghost Busters DVD',                     # Notes
        #  'n',                                     # isReconciled
        #  16.7)                                    # trxValue
        #
        # Example row(tuple) for a transaction for an account would be as follows:
        #
        # ('fff5f3783282da1b8df557655c3ed4ed',      # TrxGuid
        #  '37f277b31d319ae3969b42f60f5bf4e4',      # AccGuid
        #  'Current Account',                       # AccountName
        #  '2016-12-21 10:59:00',                   # DatePosted
        #  '',                                      # Ref
        #  'WH Smiths',                             # Description
        #  'Ghost Busters DVD',                     # Notes
        #  'y',                                     # isReconciled
        #  -16.7)                                   # trxValue

        (self.transaction_guid, self.account_guid, self.account_name, self.date_posted, self.ref, self.description,
         self.memo, is_reconciled, trx_value) = row

        self.account_splits = list()
        self.is_account_side = False

        try:
            acc = accounts[self.account_guid]

            acc_split = AccountSplit(acc, is_reconciled, trx_value)

            if acc.is_account:
                acc.transactions[self.transaction_guid] = self  # Transaction is added to the parent account
                self.is_account_side = True

            self.account_splits.append(acc_split)

        except KeyError:
            print(f'WARNING: Could not find account for transaction "{self}"! This will be ignored in the export')

    def __str__(self) -> string:
        return f'{self.date_posted} / {self.account_name} / {self.description}'

    # def __eq__(self, other):
    #     if not (isinstance(other, self.__class__)):
    #         return False
    #     if self.transaction_guid == other.transaction_guid:
    #         return True
    #     else:
    #         return False

import string


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
        (self.hierarchy, self.name, self.guid, self.description, _, self.account_type, self.hierarchy_level) = row
        self.transactions = list()

    def __str__(self) -> string:
        return f'{self.account_type} / {self.name} / {len(self.transactions)} transactions'

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
        #  None,                                    # AccGuid
        #  None,                                    # AccountName
        #  '2016-12-21 10:59:00',                   # DatePosted
        #  '',                                      # Ref
        #  'WH Smiths',                             # Description
        #  'Ghost Busters DVD',                     # Notes
        #  '0561c5ddbf424ab5ef86f6a98f6d5b03',      # CategoryGuid
        #  'DVDs',                                  # Transfer
        #  'n',                                     # isReconciled
        #  16.7)                                   # trxValue
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
        #  None,                                    # CategoryGuid
        #  None,                                    # Transfer
        #  'y',                                     # isReconciled
        #  -16.7)                                  # trxValue

        # TODO: improve tuple unpacking to only extract values needed
        (self.transaction_guid, self.account_guid, self.account_name, self.date_posted, self.ref, self.description,
         self.memo, self.category_guid, self.transfer, self.is_reconciled, self.trx_value) = row

        # TODO: The following attributes are held in the account split so don't need to be stored against Transaction:
        #           - is_reconciled
        #           - trx_value

        self.account_splits = list()
        self.parent_accounts = list()

        try:
            acc = accounts[self.account_guid] if self.account_guid is not None else accounts[self.category_guid]

            acc_split = AccountSplit(acc, self.is_reconciled, self.trx_value)

            if acc.is_account:
                acc.transactions.append(self)        # Transaction is added to the parent account...
                self.parent_accounts.append(acc)     # ... and is added to parent account reference of the transaction

            self.account_splits.append(acc_split)

        except KeyError:
            print(f'WARNING: Could not find account for transaction "{self}"! This will be ignored in the export')

    def __str__(self) -> string:
        return f'{self.date_posted} / {self.account_name} / {self.ref} / {self.description} / {self.trx_value}'

    # def __eq__(self, other):
    #     if not (isinstance(other, self.__class__)):
    #         return False
    #     if self.transaction_guid == other.transaction_guid:
    #         return True
    #     else:
    #         return False

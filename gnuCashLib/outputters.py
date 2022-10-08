import string

from gnuCashLib.data_objects import Account


def write_data(accounts: list[Account], output_file: string) -> None:
    """
    Writes all the accounts and transactions to the output file

    :param accounts: a list of accounts with transaction to output
    :param output_file: path of the output file to write the accounts and transactions to
    :return: nothing is returned, but the output_file should be produced
    """
    print(f'Writing {len(accounts)} accounts to file {output_file}')
    return

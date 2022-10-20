import argparse

from gnuCashLib.outputters import write_data
from gnuCashLib.exporter import extract_data


def configure_argparse():
    parser = argparse.ArgumentParser(description='Extract a GnuCash database and output to QIF.')
    parser.add_argument('-s', '--sqldb', help='full path to the sqlite file', required=True)
    parser.add_argument('-o', '--output', help='output file', default='.\\output.qif')
    return parser.parse_args()


def main():
    args = configure_argparse()

    # TODO: check args.sqldb file exists
    # TODO: check if args.output file exists - confirm overwrite if so

    print('')
    print('GnuCash Extractor')
    print('=================')
    print('')
    print(f'Sqlite DB:   {args.sqldb}')
    print(f'Output file: {args.output}')
    print('')

    accounts = extract_data(args.sqldb)

    print('Account/Transaction Spread')
    print('-------------------------')
    print()
    for acc in [a for a in accounts.values() if a.is_account]:
        print(acc)

    print()

    write_data(accounts, args.output)


if __name__ == '__main__':
    main()

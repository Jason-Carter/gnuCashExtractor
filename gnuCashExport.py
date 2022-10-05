import argparse

from gnuCashLib.Outputters import write_data
from gnuCashLib.Exporters import extract_data


def configure_argparse():
    parser = argparse.ArgumentParser(description='Extract a GnuCash database and output to QIF.')
    parser.add_argument('-s', '--sqldb', help='full path to the sqlite file', required=True)
    parser.add_argument('-o', '--output', help='output file', default='.\\output.qif')
    return parser.parse_args()


def main():
    args = configure_argparse()

    # TODO: check args.sqldb file exists
    # TODO: check if args.output file exists - confirm overwrite if so

    extract_data(args.sqldb)
    write_data(args.output)


if __name__ == '__main__':
    main()

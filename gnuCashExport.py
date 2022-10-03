import argparse
from Exporters.sqlLiteExporter import extract_data
from Outputters.qifOutputter import write_data


def configure_argparse():
    parser = argparse.ArgumentParser(description='Extract a GnuCash database and output to QIF.')
    parser.add_argument('-s', '--sqldb', help='full path to the sqlite file', required=True)
    parser.add_argument('-o', '--output', help='output file', default='.\\output.qif')
    return parser.parse_args()


def main():
    args = configure_argparse()
    extract_data(args.sqldb)
    write_data(args.output)


if __name__ == '__main__':
    main()

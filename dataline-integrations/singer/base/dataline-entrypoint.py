import argparse
import sys


# todo: what level do we specify tap vs target? how do we list supported commands

parent_parser = argparse.ArgumentParser(add_help=False)
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers(title='commands')

specParser = subparsers.add_parser("spec", help="outputs the json configuration specification", parents=[parent_parser])

checkParser = subparsers.add_parser("check", help="checks the config can be used to connect", parents=[parent_parser])
requiredCheckParser = checkParser.add_argument_group('required named arguments')
requiredCheckParser.add_argument('--config', type=str, required=True, help='path to the json configuration file')

discoverParser = subparsers.add_parser("discover", help="outputs a catalog describing the source's schema", parents=[parent_parser])
requiredDiscoverParser = discoverParser.add_argument_group('required named arguments')
requiredDiscoverParser.add_argument('--config', type=str, required=True, help='path to the json configuration file')
requiredDiscoverParser.add_argument('--catalog', type=str, required=True, help='output path for the discovered catalog')

readParser = subparsers.add_parser("read", help="reads the source and outputs messages to STDOUT", parents=[parent_parser])
readParser.add_argument('--state', type=str, required=True, help='path to the json-encoded state file')
requiredReadParser = readParser.add_argument_group('required named arguments')
requiredReadParser.add_argument('--config', type=str, required=True, help='path to the json configuration file')
requiredReadParser.add_argument('--catalog', type=str, required=True, help='path to the catalog used to determine which data to read')

writeParser = subparsers.add_parser("write", help="writes messages from STDIN to the integration", parents=[parent_parser])
requiredWriteParser = writeParser.add_argument_group('required named arguments')
requiredWriteParser.add_argument('--config', type=str, required=True, help='path to the json configuration file')

# todo: set up


args = main_parser.parse_args()

sys.exit(0)

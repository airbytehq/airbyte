import argparse
import sys
import enum


class DatalineEntrypointType(enum.Enum):
    SOURCE = 1
    DESTINATION = 2


class DatalineEntrypointBuilder(object):
    def __init__(self):
        self.function_map = {}

    def create_source(self, spec_handler, check_handler, discover_handler, read_handler):
        self.function_map = {
            "spec": spec_handler,
            "check": check_handler,
            "discover": discover_handler,
            "read": read_handler
        }
        self.__create_and_run_parser(DatalineEntrypointType.SOURCE);

    def create_target(self, spec_handler, check_handler, write_handler):
        self.function_map = {
            "spec": spec_handler,
            "check": check_handler,
            "write": write_handler
        }
        self.__create_and_run_parser(DatalineEntrypointType.DESTINATION);

    def __create_and_run_parser(self, entrypoint_type):
        parent_parser = argparse.ArgumentParser(add_help=False)
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(title='commands', dest='command')

        spec_parser = subparsers.add_parser("spec", help="outputs the json configuration specification", parents=[parent_parser])

        check_parser = subparsers.add_parser("check", help="checks the config can be used to connect", parents=[parent_parser])
        required_check_parser = check_parser.add_argument_group('required named arguments')
        required_check_parser.add_argument('--config', type=str, required=True, help='path to the json configuration file')

        if entrypoint_type == DatalineEntrypointType.SOURCE:
            discover_parser = subparsers.add_parser("discover", help="outputs a catalog describing the source's schema", parents=[parent_parser])
            required_discover_parser = discover_parser.add_argument_group('required named arguments')
            required_discover_parser.add_argument('--config', type=str, required=True, help='path to the json configuration file')
            required_discover_parser.add_argument('--catalog', type=str, required=True, help='output path for the discovered catalog')

            read_parser = subparsers.add_parser("read", help="reads the source and outputs messages to STDOUT", parents=[parent_parser])
            read_parser.add_argument('--state', type=str, required=True, help='path to the json-encoded state file')
            required_read_parser = read_parser.add_argument_group('required named arguments')
            required_read_parser.add_argument('--config', type=str, required=True, help='path to the json configuration file')
            required_read_parser.add_argument('--catalog', type=str, required=True, help='path to the catalog used to determine which data to read')

        if entrypoint_type == DatalineEntrypointType.DESTINATION:
            write_parser = subparsers.add_parser("write", help="writes messages from STDIN to the integration", parents=[parent_parser])
            required_write_parser = write_parser.add_argument_group('required named arguments')
            required_write_parser.add_argument('--config', type=str, required=True, help='path to the json configuration file')

        parsed_args = main_parser.parse_args()
        function = self.function_map[parsed_args.command]
        function(parsed_args)

        print("Unexpected state: integration handlers should exit.")
        sys.exit(2)

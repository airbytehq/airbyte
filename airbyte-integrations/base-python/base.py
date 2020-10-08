import argparse
import logging
import sys
import tempfile
import os.path
import importlib

from airbyte_protocol import Source

impl_module = os.environ['AIRBYTE_IMPL_MODULE']
impl_class = os.environ['AIRBYTE_IMPL_PATH']

module = importlib.import_module(impl_module)
impl = getattr(module, impl_class)

class AirbyteEntrypoint(object):
    def __init__(self, source):
        self.source = source

    def start(self):
        # set up parent parsers
        parent_parser = argparse.ArgumentParser(add_help=False)
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(title='commands', dest='command')

        # spec
        subparsers.add_parser("spec", help="outputs the json configuration specification", parents=[parent_parser])

        # check
        check_parser = subparsers.add_parser("check", help="checks the config can be used to connect",
                                             parents=[parent_parser])
        required_check_parser = check_parser.add_argument_group('required named arguments')
        required_check_parser.add_argument('--config', type=str, required=True,
                                           help='path to the json configuration file')

        # discover
        discover_parser = subparsers.add_parser("discover", help="outputs a catalog describing the source's schema",
                                                parents=[parent_parser])
        required_discover_parser = discover_parser.add_argument_group('required named arguments')
        required_discover_parser.add_argument('--config', type=str, required=True,
                                              help='path to the json configuration file')

        # read
        read_parser = subparsers.add_parser("read", help="reads the source and outputs messages to STDOUT",
                                            parents=[parent_parser])
        # todo: re-add state handling
        # read_parser.add_argument('--state', type=str, required=False, help='path to the json-encoded state file')
        required_read_parser = read_parser.add_argument_group('required named arguments')
        required_read_parser.add_argument('--config', type=str, required=True,
                                          help='path to the json configuration file')
        required_read_parser.add_argument('--catalog', type=str, required=True,
                                          help='path to the catalog used to determine which data to read')

        # parse the args
        parsed_args = main_parser.parse_args()

        # execute
        cmd = parsed_args.command

        # todo: add try catch for exceptions with different exit codes

        with tempfile.TemporaryDirectory() as temp_dir:
            if cmd == "spec":
                # todo: output this as a JSON formatted message
                print(source.spec().spec_string)
                sys.exit(0)

            rendered_config_path = os.path.join(temp_dir, 'config.json')
            config_object = source.read_config(parsed_args.config)
            source.render_config(config_object, rendered_config_path)

            # todo: output message for check
            if cmd == "check":
                check_result = source.check(logging, rendered_config_path)
                if check_result.successful:
                    print("Check succeeded")
                    sys.exit(0)
                else:
                    print("Check failed")
                    sys.exit(1)
            elif cmd == "discover":
                schema = source.discover(logging, rendered_config_path)
                print(schema.schema)
                sys.exit(0)
            elif cmd == "read":
                # todo: pass in state
                generator = source.read(logging, rendered_config_path)
                for message in generator:
                    print(message.serialize(sort_keys=True))
                sys.exit(0)
            else:
                raise Exception("Unexpected command " + cmd)


# set up and run entrypoint
source = impl()

if not isinstance(source, Source):
    raise Exception("Source implementation provided does not implement Source class!")

AirbyteEntrypoint(source).start()

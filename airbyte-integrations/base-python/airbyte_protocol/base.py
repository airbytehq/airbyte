import argparse
import sys
import tempfile
import os.path
import importlib

from . import ConfigContainer
from . import Source
from . import AirbyteLogger

AIRBYTE_IMPL_MODULE = 'AIRBYTE_IMPL_MODULE'
AIRBYTE_IMPL_PATH = 'AIRBYTE_IMPL_PATH'

logger = AirbyteLogger()

if AIRBYTE_IMPL_MODULE not in os.environ:
    impl_module = 'airbyte_protocol'
    logger.warn(f"Using default module: {impl_module}")
else:
    impl_module = os.environ[AIRBYTE_IMPL_MODULE]

if AIRBYTE_IMPL_PATH not in os.environ:
    impl_class = 'Source'
    logger.warn(f"Using default class: {impl_module}")
else:
    impl_class = os.environ[AIRBYTE_IMPL_PATH]

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

        read_parser.add_argument('--state', type=str, required=False, help='path to the json-encoded state file')
        required_read_parser = read_parser.add_argument_group('required named arguments')
        required_read_parser.add_argument('--config', type=str, required=True,
                                          help='path to the json configuration file')
        required_read_parser.add_argument('--catalog', type=str, required=True,
                                          help='path to the catalog used to determine which data to read')

        # parse the args
        parsed_args = main_parser.parse_args()

        # execute
        cmd = parsed_args.command
        if not cmd:
            raise Exception("No command passed")

        # todo: add try catch for exceptions with different exit codes

        with tempfile.TemporaryDirectory() as temp_dir:
            if cmd == "spec":
                # todo: output this as a JSON formatted message
                print(self.source.spec().spec_string)
                sys.exit(0)

            rendered_config_path = os.path.join(temp_dir, 'config.json')
            raw_config = self.source.read_config(parsed_args.config)
            rendered_config = self.source.transform_config(raw_config)
            self.source.write_config(rendered_config, rendered_config_path)

            config_container = ConfigContainer(
                raw_config=raw_config,
                rendered_config=rendered_config,
                raw_config_path=parsed_args.config,
                rendered_config_path=rendered_config_path)

            if cmd == "check":
                check_result = self.source.check(logger, config_container)
                if check_result.successful:
                    logger.info("Check succeeded")
                    sys.exit(0)
                else:
                    logger.error("Check failed")
                    sys.exit(1)
            elif cmd == "discover":
                catalog = self.source.discover(logger, config_container)
                print(catalog.serialize())
                sys.exit(0)
            elif cmd == "read":
                generator = self.source.read(logger, config_container, parsed_args.catalog, parsed_args.state)
                for message in generator:
                    print(message.serialize())
                sys.exit(0)
            else:
                raise Exception("Unexpected command " + cmd)


def main():
    # set up and run entrypoint
    source = impl()

    if not isinstance(source, Source):
        raise Exception("Source implementation provided does not implement Source class!")

    AirbyteEntrypoint(source).start()


if __name__ == "__main__":
    main()

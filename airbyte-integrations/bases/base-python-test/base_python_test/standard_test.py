#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import argparse
import importlib
import json
import os.path
import sys
from enum import Enum

from .test_iface import StandardSourceTestIface


class TestAction(Enum):
    GET_SPEC = "get_spec"
    GET_CONFIG = "get_config"
    GET_CONFIGURED_CATALOG = "get_configured_catalog"
    GET_STATE = "get_state"
    GET_REGEX_TESTS = "get_regex_tests"
    SETUP = "setup"
    TEARDOWN = "teardown"


class StandardSourceTestRunner(StandardSourceTestIface):
    OUTPUT_FILENAME = "output.json"

    def __init__(self, test):
        self.test = test

    @staticmethod
    def write_output(json, path):
        print(f"output path: {path}")
        with open(path + "/" + StandardSourceTestRunner.OUTPUT_FILENAME, "w") as fh:
            fh.write(json)

    def start(self, args):
        print("parsing")
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("command", type=TestAction, choices=TestAction)
        parser.add_argument("--out", type=str, required=False, help="path to json output")

        # parse the args
        parsed_args = parser.parse_args(args)

        # execute
        cmd = parsed_args.command

        if not cmd:
            raise Exception("No command passed")

        print(f"executing command {cmd}")
        output = None
        if cmd == TestAction.GET_SPEC:
            output = self.test.get_spec().json(exclude_unset=True)
        elif cmd == TestAction.GET_CONFIG:
            output = json.dumps(self.test.get_config())
        elif cmd == TestAction.GET_CONFIGURED_CATALOG:
            output = self.test.get_catalog().json(exclude_unset=True)
        elif cmd == TestAction.GET_STATE:
            output = json.dumps(self.test.get_state())
        elif cmd == TestAction.SETUP:
            self.test.setup()
        elif cmd == TestAction.TEARDOWN:
            self.test.teardown()
        elif cmd == TestAction.GET_REGEX_TESTS:
            output = json.dumps({"tests": self.test.get_regex_tests()})
        else:
            raise Exception("Unexpected command " + cmd)

        print("writing output")
        if output:
            StandardSourceTestRunner.write_output(output, parsed_args.out)

        print("complete")


def launch(source, args):
    StandardSourceTestRunner(source).start(args)


def main():
    impl_module = os.environ.get("AIRBYTE_TEST_MODULE")
    impl_class = os.environ.get("AIRBYTE_TEST_PATH")
    module = importlib.import_module(impl_module)
    impl = getattr(module, impl_class)

    # set up and run test runner
    test = impl()

    if not isinstance(test, StandardSourceTestIface):
        raise Exception("Test implementation provided does not implement StandardSourceTestIface class!")

    launch(test, sys.argv[1:])

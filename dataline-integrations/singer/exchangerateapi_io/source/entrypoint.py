import sys

from dataline_entrypoint import DatalineEntrypointBuilder

def spec_handler(args):
    print("spec")
    sys.exit(0)

def check_handler(args):
    print("check")
    sys.exit(0)

def discover_handler(args):
    print("discover")
    sys.exit(0)

def read_handler(args):
    print("read")
    sys.exit(0)

DatalineEntrypointBuilder().create_source(
    spec_handler, check_handler, discover_handler, read_handler
)

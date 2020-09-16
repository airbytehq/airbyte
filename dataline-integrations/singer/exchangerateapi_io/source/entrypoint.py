import os
import sys

from dataline_entrypoint import DatalineEntrypointBuilder

def spec_handler(args):
    print("spec") # todo
    sys.exit(0)

def check_handler(args):
    print("check") # todo
    sys.exit(0)

def discover_handler(args):
    exit_code = os.system("tap-exchangeratesapi | grep '\"type\": \"SCHEMA\"' | head -1 | jq -c '{\"streams\":[{\"stream\": .stream, \"schema\": .schema}]}' > " + args.catalog)
    sys.exit(exit_code)

def read_handler(args):
    exit_code = os.system(f"tap-exchangeratesapi --config {args.config}")
    sys.exit(exit_code)

DatalineEntrypointBuilder().create_source(
    spec_handler, check_handler, discover_handler, read_handler
)

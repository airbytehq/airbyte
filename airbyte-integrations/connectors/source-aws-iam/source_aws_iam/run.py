import sys
from airbyte_cdk.entrypoint import launch
from source_aws_iam import SourceAwsIam


def run():
    source = SourceAwsIam()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()

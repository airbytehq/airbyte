import sys

from airbyte_cdk.entrypoint import launch
from source_cloudwatch_logs import SourceCloudwatchLogs

if __name__ == "__main__":
    source = SourceCloudwatchLogs()
    launch(source, sys.argv[1:])

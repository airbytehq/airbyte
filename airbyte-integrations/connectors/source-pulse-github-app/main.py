# source_pulse_github_app/__main__.py
import sys
from airbyte_cdk.entrypoint import launch
from source_pulse_github_app.source import SourcePulseGithubApp

if __name__ == "__main__":
    source = SourcePulseGithubApp()
    launch(source, sys.argv[1:])

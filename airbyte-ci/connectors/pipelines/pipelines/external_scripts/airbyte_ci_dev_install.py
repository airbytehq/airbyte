# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

# !IMPORTANT! This script is used to install the airbyte-ci tool on a Linux or macOS system.
# Meaning, no external dependencies are allowed as we don't want users to have to run anything
# other than this script to install the tool.

import subprocess
import sys


def check_command_exists(command: str, not_found_message: str) -> None:
    """
    Check if a command exists in the system path.
    """
    try:
        subprocess.check_call(["which", command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print(not_found_message)
        sys.exit(1)


def main() -> None:
    # Check if Python 3.10 is on the path
    check_command_exists(
        "python3.10",
        """python3.10 not found on the path.
Please install Python 3.10 using pyenv:
1. Install pyenv if not already installed:
   brew install pyenv
2. Install Python 3.10 using pyenv:
   pyenv install 3.10.12""",
    )
    print("Python 3.10 is already installed.")

    # Check if pipx is installed
    check_command_exists(
        "pipx",
        """pipx not found. Please install pipx:
1. Ensure Python 3.6 or later is installed.
2. Install pipx using Python:
   python3 -m pip install --user pipx
3. Add pipx to your PATH:
   python3 -m pipx ensurepath
After installation, restart your terminal or source your shell
configuration file to ensure the pipx command is available.""",
    )
    print("pipx is already installed.")

    # Install airbyte-ci development version
    subprocess.run(["pipx", "install", "--editable", "--force", "--python=python3.10", "airbyte-ci/connectors/pipelines/"])
    print("Development version of airbyte-ci installed.....")


if __name__ == "__main__":
    main()

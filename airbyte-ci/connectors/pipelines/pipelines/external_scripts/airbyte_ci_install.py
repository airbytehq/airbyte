# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

# !IMPORTANT! This script is used to install the airbyte-ci tool on a Linux or macOS system.
# Meaning, no external dependencies are allowed as we don't want users to have to run anything
# other than this script to install the tool.

import os
import shutil
import sys
import tempfile
import urllib.request

# !IMPORTANT! This constant is inline here instead of being imported from pipelines/consts.py
# because we don't want to introduce any dependencies on other files in the repository.
RELEASE_URL = os.getenv("RELEASE_URL", "https://connectors.airbyte.com/files/airbyte-ci/releases")


def get_airbyte_os_name():
    """
    Returns 'ubuntu' if the system is Linux or 'macos' if the system is macOS.
    """
    OS = os.uname().sysname
    if OS == "Linux":
        print(f"Linux based system detected.")
        return "ubuntu"
    elif OS == "Darwin":
        print(f"macOS based system detected.")
        return "macos"
    else:
        return None


def main(version="latest"):
    # Determine the operating system
    os_name = get_airbyte_os_name()
    if os_name is None:
        print("Unsupported operating system")
        return

    url = f"{RELEASE_URL}/{os_name}/{version}/airbyte-ci"

    # Create the directory if it does not exist
    destination_dir = os.path.expanduser("~/.local/bin")
    os.makedirs(destination_dir, exist_ok=True)

    # Download the binary to a temporary folder
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = os.path.join(tmp_dir, "airbyte-ci")

        # Download the file using urllib.request
        print(f"Downloading from {url}")
        with urllib.request.urlopen(url) as response, open(tmp_file, "wb") as out_file:
            shutil.copyfileobj(response, out_file)

        # Check if the destination path is a symlink and delete it if it is
        destination_path = os.path.join(destination_dir, "airbyte-ci")
        if os.path.islink(destination_path):
            os.remove(destination_path)

        # Copy the file from the temporary folder to the destination
        shutil.copy(tmp_file, destination_path)

        # Make the binary executable
        os.chmod(destination_path, 0o755)

    # ASCII Art and Completion Message
    install_complete_message = f"""
    ╔───────────────────────────────────────────────────────────────────────────────╗
    │                                                                               │
    │    AAA   IIIII RRRRRR  BBBBB   YY   YY TTTTTTT EEEEEEE         CCCCC  IIIII   │
    │   AAAAA   III  RR   RR BB   B  YY   YY   TTT   EE             CC       III    │
    │  AA   AA  III  RRRRRR  BBBBBB   YYYYY    TTT   EEEEE   _____  CC       III    │
    │  AAAAAAA  III  RR  RR  BB   BB   YYY     TTT   EE             CC       III    │
    │  AA   AA IIIII RR   RR BBBBBB    YYY     TTT   EEEEEEE         CCCCC  IIIII   │
    │                                                                               │
    │  === Installation complete. v({version})===                                     │
    │  {destination_path}                                                           │
    ╚───────────────────────────────────────────────────────────────────────────────╝
    """

    print(install_complete_message)


if __name__ == "__main__":
    version_arg = sys.argv[1] if len(sys.argv) > 1 else "latest"
    main(version_arg)

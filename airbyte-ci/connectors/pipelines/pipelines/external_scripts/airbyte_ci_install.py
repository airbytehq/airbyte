# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

# !IMPORTANT! This script is used to install the airbyte-ci tool on a Linux or macOS system.
# Meaning, no external dependencies are allowed as we don't want users to have to run anything
# other than this script to install the tool.

from __future__ import annotations

import os
import shutil
import ssl
import sys
import urllib.request
from typing import TYPE_CHECKING

# !IMPORTANT! This constant is inline here instead of being imported from pipelines/consts.py
# because we don't want to introduce any dependencies on other files in the repository.
RELEASE_URL = os.getenv("RELEASE_URL", "https://connectors.airbyte.com/files/airbyte-ci/releases")

if TYPE_CHECKING:
    from typing import Optional


def _get_custom_certificate_path() -> Optional[str]:
    """
    Returns the path to the custom certificate file if certifi is installed, otherwise None.

    HACK: This is a workaround for the fact that the pyinstaller binary does not know how or where to
    find the ssl certificates file. This happens because the binary is built on a different system
    than the one it is being run on. This function will return the path to the certifi certificate file
    if it is installed, otherwise it will return None. This function is used in get_ssl_context() below.

    WHY: this works when certifi is not found:
    If you run this file directly, it will use the system python interpreter and will be able to find
    the ssl certificates file. e.g. when running in dev mode or via the makefile.

    WHY: this works when certifi is found:
    When this file is run by the pyinstaller binary, it is through the pipelines project, which has
    certifi installed. This means that when this file is run by the pyinstaller binary, it will be able
    to find the ssl certificates file in the certifi package.

    """
    # if certifi is not installed, do nothing
    try:
        import certifi

        return certifi.where()
    except ImportError:
        return None


def get_ssl_context() -> ssl.SSLContext:
    """
    Returns an ssl.SSLContext object with the custom certificate file if certifi is installed, otherwise
    returns the default ssl.SSLContext object.
    """
    certifi_path = _get_custom_certificate_path()
    if certifi_path is None:
        return ssl.create_default_context()

    return ssl.create_default_context(cafile=certifi_path)


def get_airbyte_os_name() -> Optional[str]:
    """
    Returns 'ubuntu' if the system is Linux or 'macos' if the system is macOS.
    """
    OS = os.uname().sysname
    if OS == "Linux":
        print("Linux based system detected.")
        return "ubuntu"
    elif OS == "Darwin":
        print("macOS based system detected.")
        return "macos"
    else:
        return None


def main(version: str = "latest") -> None:
    # Determine the operating system
    os_name = get_airbyte_os_name()
    if os_name is None:
        print("Unsupported operating system")
        return

    url = f"{RELEASE_URL}/{os_name}/{version}/airbyte-ci"

    # Create the directory if it does not exist
    destination_dir = os.path.expanduser("~/.local/bin")
    os.makedirs(destination_dir, exist_ok=True)

    # Set the path of the versioned binary
    versioned_path = os.path.join(destination_dir, f"airbyte-ci-{version}")

    # If the version is not explicit, delete any existing versioned binary
    if version == "latest" and os.path.exists(versioned_path):
        os.remove(versioned_path)

    # Download the versioned binary if it doesn't exist
    if not os.path.exists(versioned_path):
        # Download the file using urllib.request
        print(f"Downloading from {url}")
        ssl_context = get_ssl_context()
        with urllib.request.urlopen(url, context=ssl_context) as response, open(versioned_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)

        # Make the versioned binary executable
        os.chmod(versioned_path, 0o755)

    # Ensure that the destination path does not exist.
    destination_path = os.path.join(destination_dir, "airbyte-ci")
    if os.path.exists(destination_path):
        os.remove(destination_path)

    # Symlink the versioned binary to the destination path
    os.symlink(versioned_path, destination_path)

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

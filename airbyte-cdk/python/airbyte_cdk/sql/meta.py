# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Environment meta utils and globals.

This module contains functions for detecting environment and runtime information.
"""

from __future__ import annotations

import os
import shutil
import sys
from contextlib import suppress
from functools import lru_cache
from pathlib import Path
from platform import python_implementation, python_version, system

import requests


COLAB_SESSION_URL = "http://172.28.0.12:9000/api/sessions"
"""URL to get the current Google Colab session information."""


def get_colab_release_version() -> str | None:
    if "COLAB_RELEASE_TAG" in os.environ:
        return os.environ["COLAB_RELEASE_TAG"]

    return None


def is_ci() -> bool:
    return "CI" in os.environ


@lru_cache
def is_langchain() -> bool:
    """Return True if running in a Langchain environment.

    This checks for the presence of the 'langchain-airbyte' package.

    TODO: A more robust check would inspect the call stack or another flag to see if we are actually
          being invoked via LangChain, vs being installed side-by-side.

    This is cached for performance reasons.
    """
    return "langchain_airbyte" in sys.modules


def is_windows() -> bool:
    return system() == "Windows"


@lru_cache
def is_colab() -> bool:
    return bool(get_colab_release_version())


@lru_cache
def is_interactive() -> bool:
    try:
        if is_colab() or is_jupyter():
            return True

        if is_ci():
            return False

        return bool(
            sys.__stdin__ and sys.__stdin__.isatty() and sys.__stdout__ and sys.__stdout__.isatty()
        )
    except Exception:
        return False


@lru_cache
def is_jupyter() -> bool:
    """Return True if running in a Jupyter notebook or qtconsole.

    Will return False in Colab (use is_colab() instead).
    """
    try:
        shell = get_ipython().__class__.__name__  # type: ignore  # noqa: PGH003
    except NameError:
        return False  # If 'get_ipython' undefined, we're probably in a standard Python interpreter.

    if shell == "ZMQInteractiveShell":
        return True  # Jupyter notebook or qtconsole.

    if shell == "TerminalInteractiveShell":
        return False  # Terminal running IPython

    return False  # Other type (?)


@lru_cache
def get_notebook_name() -> str | None:
    if is_colab():
        session_info: dict | None = None
        with suppress(Exception):
            response = requests.get(COLAB_SESSION_URL)
            if response.status_code == 200:  # noqa: PLR2004  # Magic number
                session_info = response.json()[0]

        if session_info and "name" in session_info:
            return session_info["name"]

    return None


@lru_cache
def get_vscode_notebook_name() -> str | None:
    with suppress(Exception):
        import IPython  # noqa: PLC0415

        return Path(
            IPython.extract_module_locals()[1]["__vsc_ipynb_file__"],
        ).name

    return None


def is_vscode_notebook() -> bool:
    return get_vscode_notebook_name() is not None


@lru_cache
def get_python_script_name() -> str | None:
    script_name = None
    with suppress(Exception):
        script_name = sys.argv[0]  # When running a python script, this is the script name.

    if script_name:
        return Path(script_name).name

    return None


@lru_cache
def get_application_name() -> str | None:
    return get_notebook_name() or get_python_script_name() or get_vscode_notebook_name() or None


def get_python_version() -> str:
    return f"{python_version()} ({python_implementation()})"


def get_os() -> str:
    if is_colab():
        return f"Google Colab ({get_colab_release_version()})"

    return f"{system()}"


@lru_cache
def which(executable_name: str) -> Path | None:
    """Return the path to an executable which would be run if the given name were called.

    This function is a cross-platform wrapper for the `shutil.which()` function.
    """
    which_executable: str | None = None
    which_executable = shutil.which(executable_name)
    if not which_executable and is_windows():
        # Try with the .exe extension
        which_executable = shutil.which(f"{executable_name}.exe")

    return Path(which_executable) if which_executable else None


def is_docker_installed() -> bool:
    return bool(which("docker"))

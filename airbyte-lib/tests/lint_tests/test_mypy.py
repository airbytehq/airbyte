# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import subprocess

import pytest


def test_mypy_typing():
    # Run the check command
    check_result = subprocess.run(
        ["poetry", "run", "mypy", "."],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Assert that the Ruff command exited without errors (exit code 0)
    assert check_result.returncode == 0, (
        "MyPy checks failed:\n"
        + f"{check_result.stdout.decode()}\n{check_result.stderr.decode()}\n\n"
        + "Run `poetry run mypy .` to see all failures."
    )

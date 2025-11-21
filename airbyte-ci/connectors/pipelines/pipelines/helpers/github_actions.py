#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Helper functions for GitHub Actions integration."""

import os
from pathlib import Path
from typing import Any


def write_to_github_output(**kwargs: Any) -> None:
    """Write outputs to GitHub Actions GITHUB_OUTPUT file if running in CI.

    This allows subsequent workflow steps to access the outputs from this step.

    Args:
        **kwargs: Key-value pairs to write to GITHUB_OUTPUT. Values will be
                  converted to strings.

    Example:
        write_to_github_output(
            success=True,
            report_url="https://example.com/report.html",
            connector_name="source-postgres"
        )
    """
    if not kwargs:
        return

    if not os.environ.get("CI"):
        return

    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        raise RuntimeError(
            "CI is set but GITHUB_OUTPUT is undefined or empty. "
            "On GitHub Actions this should be set automatically; for local runs, "
            "unset CI or set GITHUB_OUTPUT to a writable file path."
        )

    github_output_path = Path(github_output)

    with github_output_path.open("a", encoding="utf-8") as f:
        for key, value in kwargs.items():
            value_str = str(value)
            if "\n" in value_str:
                delimiter = "EOF"
                f.write(f"{key}<<{delimiter}\n")
                f.write(value_str)
                f.write(f"\n{delimiter}\n")
            else:
                f.write(f"{key}={value_str}\n")

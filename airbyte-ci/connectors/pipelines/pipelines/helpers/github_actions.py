#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Helper functions for GitHub Actions integration."""

import os
from pathlib import Path
from typing import Any, Dict


def write_to_github_output(outputs: Dict[str, Any]) -> None:
    """Write outputs to GitHub Actions GITHUB_OUTPUT file if running in CI.

    This allows subsequent workflow steps to access the outputs from this step.

    Args:
        outputs: Dictionary of key-value pairs to write to GITHUB_OUTPUT.
                 Values will be converted to strings.

    Example:
        write_to_github_output({
            "success": True,
            "report_url": "https://example.com/report.html",
            "connector_name": "source-postgres"
        })
    """
    if not os.environ.get("CI"):
        return

    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        return

    github_output_path = Path(github_output)

    with github_output_path.open("a") as f:
        for key, value in outputs.items():
            value_str = str(value)
            if "\n" in value_str:
                delimiter = "EOF"
                f.write(f"{key}<<{delimiter}\n")
                f.write(value_str)
                f.write(f"\n{delimiter}\n")
            else:
                f.write(f"{key}={value_str}\n")

#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Helper functions for GitHub Actions integration."""

import os
from pathlib import Path
from typing import Any, Dict, Optional


def write_to_github_output(outputs: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
    """Write outputs to GitHub Actions GITHUB_OUTPUT file if running in CI.

    This allows subsequent workflow steps to access the outputs from this step.
    This function is fail-safe and will silently return if GITHUB_OUTPUT is not
    accessible, ensuring that report saving never fails due to output writing issues.

    Args:
        outputs: Optional dictionary of key-value pairs to write to GITHUB_OUTPUT.
                 Values will be converted to strings.
        **kwargs: Additional key-value pairs to write. These will be merged with
                  outputs dict, with kwargs taking precedence.

    Example:
        write_to_github_output({
            "success": True,
            "report_url": "https://example.com/report.html"
        })

        write_to_github_output(
            success=True,
            report_url="https://example.com/report.html",
            connector_name="source-postgres"
        )

        write_to_github_output(
            {"success": False},
            success=True  # This will override the dict value
        )
    """
    if not os.environ.get("CI"):
        return

    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        return

    github_output_path = Path(github_output)

    if not github_output_path.exists() or not github_output_path.is_file():
        return

    all_outputs = {}
    if outputs:
        all_outputs.update(outputs)
    all_outputs.update(kwargs)

    try:
        with github_output_path.open("a", encoding="utf-8") as f:
            for key, value in all_outputs.items():
                value_str = str(value)
                if "\n" in value_str:
                    delimiter = "EOF"
                    f.write(f"{key}<<{delimiter}\n")
                    f.write(value_str)
                    f.write(f"\n{delimiter}\n")
                else:
                    f.write(f"{key}={value_str}\n")
    except OSError:
        return

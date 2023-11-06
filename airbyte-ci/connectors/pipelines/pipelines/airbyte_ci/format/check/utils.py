# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Dict, Tuple

from jinja2 import Template

SUMMARY_TEMPLATE_STR = """

Summary of Check Results
========================
{% for command_name, result in check_results.items() %}
{{ '✅' if result[0] else '❌' }} {{ command_prefix }} {{ command_name }}
{% endfor %}
"""

DETAILS_TEMPLATE_STR = """

Detailed Errors for Failed Checks
=================================
{% for command_name, error in failed_commands_details %}
❌ {{ command_prefix }} {{ command_name }}

Error: {{ error }}
{% endfor %}
=================================

"""


def log_output(check_results: Dict[str, Tuple[bool, str]], list_errors, logger):
    command_prefix = "airbyte-ci check"

    summary_template = Template(SUMMARY_TEMPLATE_STR)
    summary_message = summary_template.render(check_results=check_results, command_prefix=command_prefix)
    logger.info(summary_message)

    result_contains_failures = any(not succeeded for (succeeded, _) in check_results.values())

    if result_contains_failures:
        if list_errors:
            failed_commands_details = [(name, error) for name, (success, error) in check_results.items() if not success]
            if failed_commands_details:
                details_template = Template(DETAILS_TEMPLATE_STR)
                details_message = details_template.render(failed_commands_details=failed_commands_details, command_prefix=command_prefix)
                logger.info(details_message)
        else:
            logger.info("Run `airbyte-ci format check --list-errors` to see detailed error messages for failed checks.")

        logger.info("Run `airbyte-ci format fix` to fix formatting errors.")

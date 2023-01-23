#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys

def check_documentation_markdown_file(connector_name: str) -> bool:
    """Check if a markdown file with connector documentation is available 
    in docs/integrations/<connector-type>/<connector-name>.md

    Args:
        connector_name (str): The connector name

    Returns:
        bool: Wether a documentation file was found.
    """
    # TODO implement
    return True

def check_changelog_entry_is_updated(connector_name: str) -> bool:
    """Check that the changelog entry is updated for the latest connector version
    in docs/integrations/<connector-type>/<connector-name>.md

    Args:
        connector_name (str): The connector name

    Returns:
        bool: Wether a the changelog is up to date.
    """
    # TODO implement
    return True

def check_connector_icon_is_available(connector_name: str) -> bool:
    """Check an SVG icon exists for a connector in
    in airbyte-config/init/src/main/resources/icons/<connector-name>.svg

    Args:
        connector_name (str): The connector name

    Returns:
        bool: Wether an icon exists for this connector.
    """
    # TODO implement
    return True

def check_connector_https_url_only(connector_name: str) -> bool:
    """Check a connector code contains only https url.

    Args:
        connector_name (str): The connector name

    Returns:
        bool: Wether the connector code contains only https url.
    """
    # TODO implement
    return True

def check_connector_has_no_critical_vulnerabilities(connector_name: str) -> bool:
    """Check if the connector image is free of critical Snyk vulnerabilities.
    Runs a docker scan command.

    Args:
        connector_name (str): The connector name

    Returns:
        bool: Wether the connector is free of critical vulnerabilities.
    """
    # TODO implement
    return True

QA_CHECKS = [
    check_documentation_markdown_file,
    check_changelog_entry_is_updated,
    check_connector_icon_is_available,
    check_connector_https_url_only,
    check_connector_has_no_critical_vulnerabilities
]

def run_qa_checks():
    connector_name = sys.argv[1]
    print(f"Running QA checks for {connector_name}")
    qa_check_results = {qa_check.__name__: qa_check(connector_name) for qa_check in QA_CHECKS}
    if not all(qa_check_results.values()):
        print(f"QA checks failed for {connector_name}")
        for check_name, check_result in qa_check_results.items():
            check_result_prefix = "✅" if check_result else "❌"
            print(f"{check_result_prefix} - {check_name}")
        sys.exit(1)
    else:
        print(f"All QA checks succeeded for {connector_name}")
        sys.exit(0)

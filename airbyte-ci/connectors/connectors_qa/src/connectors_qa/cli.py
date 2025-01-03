# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Dict, Iterable, List

import asyncclick as click
import asyncer
from connector_ops.utils import Connector  # type: ignore
from jinja2 import Environment, PackageLoader, select_autoescape

from connectors_qa.checks import ENABLED_CHECKS
from connectors_qa.consts import CONNECTORS_QA_DOC_TEMPLATE_NAME
from connectors_qa.models import Check, CheckCategory, CheckResult, CheckStatus, Report
from connectors_qa.utils import get_all_connectors_in_directory, remove_strict_encrypt_suffix


# HELPERS
async def run_checks_for_connector(check_to_run: Iterable[Check], connector: Connector) -> List[CheckResult]:
    soon_check_results = []
    async with asyncer.create_task_group() as check_task_group:
        for check in check_to_run:
            soon_check_results.append(check_task_group.soonify(asyncer.asyncify(check.run))(connector))
    check_results = [r.value for r in soon_check_results]
    for check_result in check_results:
        click.echo(check_result, err=check_result.status is CheckStatus.FAILED)
    return check_results


@click.group
async def connectors_qa() -> None:
    pass


@connectors_qa.command("run", help="Run the QA checks on the given connectors.")
@click.option(
    "-c",
    "--check",
    "selected_checks",
    multiple=True,
    type=click.Choice([type(check).__name__ for check in ENABLED_CHECKS]),
)
@click.option(
    "-n",
    "--name",
    "selected_connectors",
    multiple=True,
    help="The technical name of the connector. e.g. 'source-google-sheets'.",
)
@click.option(
    "-d",
    "--connector-directory",
    "connector_directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="The directory containing the connectors, to run the checks on all connectors in this directory.",
)
@click.option(
    "-r",
    "--report-path",
    "report_path",
    type=click.Path(file_okay=True, path_type=Path, writable=True, dir_okay=False),
    help="The path to the report file to write the results to as JSON.",
)
async def run(
    selected_checks: List[str],
    selected_connectors: List[str],
    connector_directory: Path | None,
    report_path: Path | None,
) -> None:
    checks_to_run = [check for check in ENABLED_CHECKS if type(check).__name__ in selected_checks] if selected_checks else ENABLED_CHECKS
    connectors: List[Connector] = []
    if selected_connectors:
        connectors += [Connector(remove_strict_encrypt_suffix(connector)) for connector in selected_connectors]
    if connector_directory:
        connectors += get_all_connectors_in_directory(connector_directory)

    connectors = sorted(list(connectors), key=lambda connector: connector.technical_name)

    if not connectors:
        raise click.UsageError(
            "No connectors passed. Please pass at least one connector with --name or a directory containing connectors with --connector-directory."
        )
    soon_all_connector_check_results = []
    async with asyncer.create_task_group() as connector_task_group:
        for connector in connectors:
            soon_all_connector_check_results.append(connector_task_group.soonify(run_checks_for_connector)(checks_to_run, connector))
    all_connector_check_results = []
    for soon_connectors_check_results in soon_all_connector_check_results:
        all_connector_check_results.extend(soon_connectors_check_results.value)

    if report_path:
        Report(check_results=all_connector_check_results).write(report_path)
        click.echo(f"Report written to {report_path}")
    failed_checks = [check_result for check_result in all_connector_check_results if check_result.status is CheckStatus.FAILED]
    if failed_checks:
        raise click.ClickException(f"{len(failed_checks)} checks failed")


@connectors_qa.command("generate-documentation", help="Generate the documentation for the QA checks.")
@click.argument("output_file", type=click.Path(writable=True, dir_okay=False, path_type=Path))
async def generate_documentation(output_file: Path) -> None:
    checks_by_category: Dict[CheckCategory, List[Check]] = {}
    for check in ENABLED_CHECKS:
        checks_by_category.setdefault(check.category, []).append(check)

    jinja_env = Environment(
        loader=PackageLoader(__package__, "templates"),
        autoescape=select_autoescape(),
        trim_blocks=False,
        lstrip_blocks=True,
    )
    template = jinja_env.get_template(CONNECTORS_QA_DOC_TEMPLATE_NAME)
    documentation = template.render(checks_by_category=checks_by_category)
    output_file.write_text(documentation)
    click.echo(f"Documentation written to {output_file}")

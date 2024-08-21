# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import datetime
import itertools
import json
import logging
import re
from typing import TYPE_CHECKING

import requests
from connectors_insights.hacks import get_ci_on_master_report
from connectors_insights.models import ConnectorInsights
from connectors_insights.pylint import get_pylint_output
from connectors_insights.result_backends import FileToPersist, ResultBackend

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

    import dagger
    from anyio import Semaphore
    from connector_ops.utils import Connector  # type: ignore


def get_manifest_inferred_insights(connector: Connector) -> dict:
    if connector.manifest_path is None or not connector.manifest_path.exists():
        return {}

    manifest = connector.manifest_path.read_text()

    schemas_directory = connector.code_directory / connector.technical_name.replace("-", "_") / "schemas"

    return {
        "manifest_uses_parameters": manifest.find("$parameters") != -1,
        "manifest_uses_custom_components": manifest.find("class_name:") != -1,
        "manifest_custom_component_classes": re.findall(r"class_name: (.+)", manifest),
        "has_json_schemas": schemas_directory.is_dir() and any(schemas_directory.iterdir()),
    }


def get_metadata_inferred_insights(connector: Connector) -> Dict:
    return {
        "connector_technical_name": connector.technical_name,
        "connector_version": connector.version,
        "connector_image_address": connector.image_address,
        "uses_base_image": connector.uses_base_image,
        "base_image_address": connector.base_image_address,
        "base_image_version": connector.base_image_version,
        "connector_language": connector.language,
        "cdk_name": connector.cdk_name,
        "is_using_poetry": connector.is_using_poetry,
        "connector_definition_id": connector.metadata.get("definitionId"),
        "connector_type": connector.metadata.get("connectorType"),
        "connector_subtype": connector.metadata.get("connectorSubtype"),
        "connector_support_level": connector.metadata.get("supportLevel"),
        "ab_internal_sl": connector.metadata.get("ab_internal", {}).get("sl"),
        "ab_internal_ql": connector.metadata.get("ab_internal", {}).get("ql"),
        "is_cloud_enabled": connector.metadata.get("registryOverrides", {}).get("cloud", {}).get("enabled", False),
        "is_oss_enabled": connector.metadata.get("registryOverrides", {}).get("oss", {}).get("enabled", False),
    }


def get_sbom_inferred_insights(raw_sbom: str | None, connector: Connector) -> Dict:
    """Parse the SBOM and get dependencies and CDK version from it.

    Args:
        raw_sbom (str | None): the SBOM in JSON format.
        connector (Connector): the connector to get insights for.

    Returns:
        Dict: the inferred insights from the SBOM.
    """
    sbom_inferred_insights: Dict[str, List[Dict[str, str]] | None] = {
        "cdk_version": None,
        "dependencies": [],
    }
    if not raw_sbom:
        return sbom_inferred_insights
    sbom = json.loads(raw_sbom)
    python_artifacts = {package["name"]: package for package in sbom["packages"] if package["SPDXID"].startswith("SPDXRef-Package-python-")}
    sbom_inferred_insights["cdk_version"] = python_artifacts.get("airbyte-cdk", {}).get("versionInfo")

    for package in sbom["packages"]:
        package_type = package["SPDXID"].split("-")[2]
        try:
            dependency = {"type": package_type, "version": package["versionInfo"], "package_name": package["name"]}
        except KeyError:
            continue
        if isinstance(sbom_inferred_insights["dependencies"], list) and dependency not in sbom_inferred_insights["dependencies"]:
            sbom_inferred_insights["dependencies"].append(dependency)
    return sbom_inferred_insights


def get_pylint_inferred_insights(pylint_output: str | None) -> Dict:
    """Make insights from the pylint output.
    It currently parses the deprecated classes and modules from the pylint output.
    """
    if not pylint_output:
        return {}

    deprecated_classes_in_use = []
    deprecated_modules_in_use = []
    forbidden_method_names_in_use = []
    deprecated_class_pattern = r"Using deprecated class (\w+) of module ([\w\.]+)"
    deprecated_module_pattern = r"Deprecated module '([^']+)'"
    forbidden_method_name_pattern = r'Method name "([^"]+)"'
    for message in json.loads(pylint_output):
        if message["symbol"] == "deprecated-class":
            if match := re.search(deprecated_class_pattern, message["message"]):
                deprecated_classes_in_use.append(f"{match.group(2)}.{match.group(1)}")
        if message["symbol"] == "deprecated-module":
            if match := re.search(deprecated_module_pattern, message["message"]):
                deprecated_modules_in_use.append(match.group(1))
        if message["symbol"] == "forbidden-method-name":
            if match := re.search(forbidden_method_name_pattern, message["message"]):
                forbidden_method_names_in_use.append(match.group(1))
    return {
        "deprecated_classes_in_use": deprecated_classes_in_use,
        "deprecated_modules_in_use": deprecated_modules_in_use,
        "forbidden_method_names_in_use": forbidden_method_names_in_use,
    }


def should_skip_generation(
    result_backends: List[ResultBackend] | None, connector: Connector, files_to_persist: List[FileToPersist], rewrite: bool
) -> bool:
    """Check if the insights generation should be skipped because they already exist.
    Always run if rewrite is True or no result backends are provided.

    Args:
        result_backends (List[ResultBackend] | None): The result backends to check if the insights already exist.
        connector (Connector): The connector to check if the insights already exist.
        files_to_persist (List[FileToPersist]): The files to persist for the connector.
        rewrite (bool): Whether to rewrite the insights if they already exist.

    Returns:
        bool: True if the insights generation should be skipped, False otherwise.
    """
    if rewrite or not result_backends:
        return False

    for result_backend, file_to_persist in itertools.product(result_backends, files_to_persist):
        if not result_backend.artifact_already_exists(connector, file_to_persist):
            return False
    return True


def fetch_sbom(connector: Connector) -> str | None:
    """Fetch the SBOM for the connector if it is released.
    SBOM are generated from published Docker images. If the connector is not released it does not have a published Docker image.

    Args:
        dagger_client (dagger.Client): The Dagger client to use.
        connector (Connector): The connector to fetch the SBOM for.

    Returns:
        str | None: The SBOM in JSON format if the connector is released, None otherwise.
    """
    if connector.sbom_url:
        r = requests.get(connector.sbom_url)
        r.raise_for_status()
        return r.text
    return None


def generate_insights(connector: Connector, sbom: str | None, pylint_output: str | None) -> ConnectorInsights:
    """Generate insights for the connector.

    Args:
        connector (Connector): The connector to generate insights for.
        sbom (str | None): The SBOM in JSON format.

    Returns:
        ConnectorInsights: The insights for the connector.
    """
    ci_on_master_report = get_ci_on_master_report(connector)
    return ConnectorInsights(
        **{
            **get_metadata_inferred_insights(connector),
            **get_manifest_inferred_insights(connector),
            **get_pylint_inferred_insights(pylint_output),
            **get_sbom_inferred_insights(sbom, connector),
            "ci_on_master_report": ci_on_master_report,
            "ci_on_master_passes": ci_on_master_report.get("success") if ci_on_master_report else None,
            "insight_generation_timestamp": datetime.datetime.utcnow(),
        }
    )


# TODO: make it async for concurrent uploads
def persist_files(
    connector: Connector,
    files_to_persist: List[FileToPersist],
    result_backends: List[ResultBackend] | None,
    rewrite: bool,
    logger: logging.Logger,
) -> None:
    """Persist the files to the result backends.

    Args:
        connector (Connector): The connector to persist the files for.
        files_to_persist (List[FileToPersist]): The files to persist for the connector.
        result_backends (List[ResultBackend] | None): The result backends to persist the files to.
        rewrite (bool): Whether to rewrite the files if they already exist.
        logger (logging.Logger): The logger to use.

    Returns:
        None
    """
    if not result_backends:
        logger.warning(f"No result backends provided to persist files for {connector.technical_name}")
        return None
    for backend, file in itertools.product(result_backends, files_to_persist):
        if file.file_content:
            if not rewrite and backend.artifact_already_exists(connector, file):
                logger.info(f"Skipping writing {file.file_name} for {connector.technical_name} because it already exists.")
                continue
            backend.write(connector, file)
        else:
            logger.warning(f"No content provided for {file.file_name} for {connector.technical_name}")


async def generate_insights_for_connector(
    dagger_client: dagger.Client,
    connector: Connector,
    semaphore: Semaphore,
    rewrite: bool = False,
    result_backends: List[ResultBackend] | None = None,
) -> Tuple[bool, Connector]:
    """Aggregate insights for a connector and write them to the result backends.

    Args:
        dagger_client (dagger.Client): the dagger client.
        connector (Connector): the connector to generate insights for.
        semaphore (Semaphore): the semaphore to limit the number of concurrent insights generation.
        rewrite (bool): whether to rewrite the insights if they already exist.
        result_backend (List[ResultBackend] | None): the result backends to write the insights to.
    Returns:
        Tuple[bool, Connector]: a tuple of whether the insights were generated and the connector.
    """
    logger = logging.getLogger(__name__)
    insights_file = FileToPersist("insights.json")
    files_to_persist = [insights_file]

    async with semaphore:
        if should_skip_generation(result_backends, connector, files_to_persist, rewrite):
            logger.info(f"Skipping insights generation for {connector.technical_name} because it is already generated.")
            return True, connector

        logger.info(f"Generating insights for {connector.technical_name}")
        result_backends = result_backends or []
        try:
            pylint_output = await get_pylint_output(dagger_client, connector)
            raw_sbom = fetch_sbom(connector)
            insights = generate_insights(connector, raw_sbom, pylint_output)
            insights_file.set_file_content(insights.json())
            persist_files(connector, files_to_persist, result_backends, rewrite, logger)
            logger.info(f"Finished generating insights for {connector.technical_name}")
            return True, connector
        except Exception as e:
            logger.error(f"Failed to generate insights for {connector.technical_name}: {e}")
            return False, connector

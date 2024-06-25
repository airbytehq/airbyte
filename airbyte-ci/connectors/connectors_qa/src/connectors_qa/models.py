# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from connector_ops.utils import Connector, ConnectorLanguage  # type: ignore
from connectors_qa import consts

ALL_LANGUAGES = [
    ConnectorLanguage.JAVA,
    ConnectorLanguage.LOW_CODE,
    ConnectorLanguage.PYTHON,
]

ALL_TYPES = ["source", "destination"]


class CheckCategory(Enum):
    """The category of a QA check"""

    PACKAGING = "📦 Packaging"
    DOCUMENTATION = "📄 Documentation"
    ASSETS = "💼 Assets"
    SECURITY = "🔒 Security"
    METADATA = "📝 Metadata"
    TESTING = "🧪 Testing"


class CheckStatus(Enum):
    """The status of a QA check"""

    PASSED = "✅ Passed"
    FAILED = "❌ Failed"
    SKIPPED = "🔶 Skipped"


@dataclass
class CheckResult:
    """The result of a QA check

    Attributes:
        check (Check): The QA check that was run
        connector (Connector): The connector that was checked
        status (CheckStatus): The status of the check
        message (str): A message explaining the result of the check
    """

    check: Check
    connector: Connector
    status: CheckStatus
    message: str

    def __repr__(self) -> str:
        return f"{self.connector} - {self.status.value} - {self.check.name}: {self.message}."


class Check(ABC):

    requires_metadata: bool = True
    runs_on_released_connectors: bool = True

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the QA check

        Raises:
            NotImplementedError: Subclasses must implement name property/attribute

        Returns:
            str: The name of the QA check
        """
        raise NotImplementedError("Subclasses must implement name property/attribute")

    @property
    def required(self) -> bool:
        """Whether the QA check is required

        Returns:
            bool: Whether the QA check is required
        """
        return True

    @property
    @abstractmethod
    def description(self) -> str:
        """A full description of the QA check. Used for documentation purposes.
        It can use markdown syntax.

        Raises:
            NotImplementedError: Subclasses must implement description property/attribute

        Returns:
            str: The description of the QA check
        """
        raise NotImplementedError("Subclasses must implement description property/attribute")

    @property
    def applies_to_connector_languages(self) -> List[ConnectorLanguage]:
        """The connector languages that the QA check applies to

        Raises:
            NotImplementedError: Subclasses must implement applies_to_connector_languages property/attribute

        Returns:
            List[ConnectorLanguage]: The connector languages that the QA check applies to
        """
        return ALL_LANGUAGES

    @property
    def applies_to_connector_types(self) -> List[str]:
        """The connector types that the QA check applies to

        Returns:
            List[str]: The connector types that the QA check applies to
        """
        return ALL_TYPES

    @property
    @abstractmethod
    def category(self) -> CheckCategory:
        """The category of the QA check

        Raises:
            NotImplementedError: Subclasses must implement category property/attribute

        Returns:
            CheckCategory: The category of the QA check
        """
        raise NotImplementedError("Subclasses must implement category property/attribute")

    @property
    def applies_to_connector_support_levels(self) -> Optional[List[str]]:
        """The connector's support levels that the QA check applies to

        Returns:
            List[str]: None if connector's support levels that the QA check applies to is not specified
        """
        return None

    @property
    def applies_to_connector_cloud_usage(self) -> Optional[List[str]]:
        """The connector's cloud usage level that the QA check applies to

        Returns:
            List[str]: None if connector's cloud usage levels that the QA check applies to is not specified
        """
        return None

    def run(self, connector: Connector) -> CheckResult:
        if not self.runs_on_released_connectors and connector.is_released:
            return self.skip(
                connector,
                "Check does not apply to released connectors",
            )
        if not connector.metadata and self.requires_metadata:
            return self.fail(
                connector,
                f"This checks requires metadata file to run. Please add {consts.METADATA_FILE_NAME} file to the connector code directory.",
            )
        if not connector.language:
            return self.fail(connector, "Connector language could not be inferred")
        if connector.language not in self.applies_to_connector_languages:
            return self.skip(
                connector,
                f"Check does not apply to {connector.language.value} connectors",
            )
        if connector.connector_type not in self.applies_to_connector_types:
            return self.skip(
                connector,
                f"Check does not apply to {connector.connector_type} connectors",
            )
        if self.applies_to_connector_support_levels and connector.support_level not in self.applies_to_connector_support_levels:
            return self.skip(
                connector,
                f"Check does not apply to {connector.support_level} connectors",
            )
        if self.applies_to_connector_cloud_usage and connector.cloud_usage not in self.applies_to_connector_cloud_usage:
            return self.skip(
                connector,
                f"Check does not apply to {connector.cloud_usage} connectors",
            )
        return self._run(connector)

    def _run(self, connector: Connector) -> CheckResult:
        raise NotImplementedError("Subclasses must implement run method")

    def pass_(self, connector: Connector, message: str) -> CheckResult:
        return CheckResult(connector=connector, check=self, status=CheckStatus.PASSED, message=message)

    def fail(self, connector: Connector, message: str) -> CheckResult:
        return CheckResult(connector=connector, check=self, status=CheckStatus.FAILED, message=message)

    def skip(self, connector: Connector, reason: str) -> CheckResult:
        return CheckResult(connector=connector, check=self, status=CheckStatus.SKIPPED, message=reason)

    def create_check_result(self, connector: Connector, passed: bool, message: str) -> CheckResult:
        status = CheckStatus.PASSED if passed else CheckStatus.FAILED
        return CheckResult(check=self, connector=connector, status=status, message=message)


@dataclass
class Report:
    """The connectors_report of a QA run

    Attributes:
        check_results (List[CheckResult]): The results of the QA checks
    """

    badge_name = "Connector QA Checks"
    check_results: list[CheckResult]
    image_shield_root_url = "https://img.shields.io/badge"

    def write(self, output_file: Path) -> None:
        """Write the connectors_report to a file

        Args:
            output_file (Path): The file to write the connectors_report to
        """
        output_file.write_text(self.to_json())

    def to_json(self) -> str:
        """Convert the connectors_report to a JSON-serializable dictionary

        Returns:
            str: The connectors_report as a JSON string
        """
        connectors_report: Dict[str, Dict] = {}
        for check_result in self.check_results:
            connector = check_result.connector
            connectors_report.setdefault(
                connector.technical_name,
                {
                    "failed_checks": [],
                    "skipped_checks": [],
                    "passed_checks": [],
                    "failed_checks_count": 0,
                    "skipped_checks_count": 0,
                    "successful_checks_count": 0,
                    "total_checks_count": 0,
                },
            )
            check_name_and_message = {
                "check": check_result.check.name,
                "message": check_result.message,
            }
            if check_result.status == CheckStatus.PASSED:
                connectors_report[connector.technical_name]["passed_checks"].append(check_name_and_message)
                connectors_report[connector.technical_name]["successful_checks_count"] += 1
                connectors_report[connector.technical_name]["total_checks_count"] += 1

            elif check_result.status == CheckStatus.FAILED:
                connectors_report[connector.technical_name]["failed_checks"].append(check_name_and_message)
                connectors_report[connector.technical_name]["failed_checks_count"] += 1
                connectors_report[connector.technical_name]["total_checks_count"] += 1

            elif check_result.status == CheckStatus.SKIPPED:
                connectors_report[connector.technical_name]["skipped_checks"].append(check_name_and_message)
                connectors_report[connector.technical_name]["skipped_checks_count"] += 1
            else:
                raise ValueError(f"Invalid check status {check_result.status}")
        for connector_technical_name in connectors_report.keys():
            connectors_report[connector_technical_name]["badge_color"] = (
                "red" if connectors_report[connector_technical_name]["failed_checks_count"] > 0 else "green"
            )
            badge_name = self.badge_name.replace(" ", "_")
            badge_text = f"{connectors_report[connector_technical_name]['successful_checks_count']}/{connectors_report[connector_technical_name]['total_checks_count']}".replace(
                " ", "_"
            )
            connectors_report[connector_technical_name]["badge_text"] = badge_text
            connectors_report[connector_technical_name][
                "badge_url"
            ] = f"{self.image_shield_root_url}/{badge_name}-{badge_text}-{connectors_report[connector_technical_name]['badge_color']}"
        return json.dumps(
            {
                "generation_timestamp": datetime.utcnow().isoformat(),
                "connectors": connectors_report,
            }
        )

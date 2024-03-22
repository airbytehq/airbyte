# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from connector_ops.utils import Connector  # type: ignore
from connectors_qa.models import Check, CheckCategory, CheckResult


class AssetsCheck(Check):
    category = CheckCategory.ASSETS


class CheckConnectorIconIsAvailable(AssetsCheck):
    name = "Connectors must have an icon"
    description = "Each connector must have an icon available in at the root of the connector code directory. It must be an SVG file named `icon.svg` and must be a square."
    requires_metadata = False

    def _run(self, connector: Connector) -> CheckResult:
        if not connector.icon_path or not connector.icon_path.exists():
            return self.create_check_result(
                connector=connector,
                passed=False,
                message="Icon file is missing. Please create an icon file at the root of the connector code directory.",
            )
        if not connector.icon_path.name == "icon.svg":
            return self.create_check_result(
                connector=connector,
                passed=False,
                message="Icon file is not named 'icon.svg'",
            )
        # TODO check that the icon is a square
        return self.create_check_result(connector=connector, passed=True, message="Icon file exists")


ENABLED_CHECKS = [CheckConnectorIconIsAvailable()]

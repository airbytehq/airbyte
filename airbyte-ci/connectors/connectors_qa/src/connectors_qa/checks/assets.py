# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from connector_ops.utils import Connector  # type: ignore

from connectors_qa.models import Check, CheckCategory, CheckResult

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Tuple

DEFAULT_AIRBYTE_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="250" height="250" fill="none">
    <path fill="#e8e8ed" fill-rule="evenodd" d="M95.775 53.416c20.364-22.88 54.087-29.592 81.811-16.385 36.836 17.549 50.274 62.252 30.219 96.734l-45.115 77.487a18.994 18.994 0 0 1-11.536 8.784 19.12 19.12 0 0 1-14.412-1.878l54.62-93.829c14.55-25.027 4.818-57.467-21.888-70.24-20.038-9.583-44.533-4.795-59.336 11.685a50.008 50.008 0 0 0-12.902 32.877 49.989 49.989 0 0 0 16.664 37.87l-31.887 54.875a18.917 18.917 0 0 1-4.885 5.534 19.041 19.041 0 0 1-6.647 3.255 19.13 19.13 0 0 1-7.395.482 19.087 19.087 0 0 1-7.018-2.365l34.617-59.575a68.424 68.424 0 0 1-10.524-23.544l-21.213 36.579a18.994 18.994 0 0 1-11.535 8.784A19.123 19.123 0 0 1 33 158.668l54.856-94.356a70.296 70.296 0 0 1 7.919-10.896Zm63.314 30.034c13.211 7.577 17.774 24.427 10.13 37.54l-52.603 90.251a18.997 18.997 0 0 1-11.536 8.784 19.122 19.122 0 0 1-14.412-1.878l48.843-84.024a27.778 27.778 0 0 1-10.825-4.847 27.545 27.545 0 0 1-7.783-8.907 27.344 27.344 0 0 1-3.307-11.326 27.293 27.293 0 0 1 1.776-11.66 27.454 27.454 0 0 1 6.533-9.846 27.703 27.703 0 0 1 10.087-6.222 27.858 27.858 0 0 1 23.097 2.135Zm-19.134 16.961a8.645 8.645 0 0 0-2.232 2.529h-.003a8.565 8.565 0 0 0 .632 9.556 8.68 8.68 0 0 0 4.097 2.915 8.738 8.738 0 0 0 5.036.163 8.692 8.692 0 0 0 4.279-2.642 8.59 8.59 0 0 0 2.079-4.558 8.563 8.563 0 0 0-.821-4.938 8.645 8.645 0 0 0-3.444-3.652 8.72 8.72 0 0 0-6.586-.86 8.7 8.7 0 0 0-3.037 1.487Z" clip-rule="evenodd"/>
</svg>"""


class AssetsCheck(Check):
    category = CheckCategory.ASSETS


class CheckConnectorIconIsAvailable(AssetsCheck):
    name = "Connectors must have an icon"
    description = "Each connector must have an icon available in at the root of the connector code directory. It must be an SVG file named `icon.svg` and must be a square."
    requires_metadata = False

    def _check_is_valid_svg(self, icon_path: Path) -> Tuple[bool, str | None]:
        try:
            # Ensure the file has an .svg extension
            if not icon_path.suffix.lower() == ".svg":
                return False, "Icon file is not a SVG file"

            # Parse the file as XML
            tree = ET.parse(icon_path)
            root = tree.getroot()

            # Check if the root tag is an 'svg' element
            if root.tag == "{http://www.w3.org/2000/svg}svg":
                return True, None
            else:
                return False, "Icon file is not a valid SVG file"
        except (ET.ParseError, FileNotFoundError):
            # If parsing fails or file not found, it's not a valid SVG
            return False, "Icon file is not a valid SVG file"

    def _run(self, connector: Connector) -> CheckResult:
        if not connector.icon_path or not connector.icon_path.exists():
            return self.create_check_result(
                connector=connector,
                passed=False,
                message="Icon file is missing. Please create an icon file at the root of the connector code directory",
            )
        is_valid_svg, error_message = self._check_is_valid_svg(connector.icon_path)
        if not is_valid_svg:
            assert error_message is not None
            return self.create_check_result(
                connector=connector,
                passed=False,
                message=error_message,
            )
        if connector.icon_path.read_text().strip().lower() == DEFAULT_AIRBYTE_ICON.strip().lower():
            return self.create_check_result(
                connector=connector,
                passed=False,
                message="Icon file is the default Airbyte icon. Please replace it with a custom square icon",
            )

        # TODO check that the icon is a square
        return self.create_check_result(connector=connector, passed=True, message="Icon file is a valid SVG file")


ENABLED_CHECKS = [CheckConnectorIconIsAvailable()]

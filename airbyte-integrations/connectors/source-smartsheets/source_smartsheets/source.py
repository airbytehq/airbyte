#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from collections.abc import Mapping
from typing import Any

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .sheet import SmartSheetAPIWrapper
from .streams import SmartsheetStream


class SourceSmartsheets(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> tuple[bool, any]:
        sheet = SmartSheetAPIWrapper(config)
        return sheet.check_connection(logger)

    def streams(self, config: Mapping[str, Any]) -> list["Stream"]:
        sheet = SmartSheetAPIWrapper(config)
        return [SmartsheetStream(sheet, config)]

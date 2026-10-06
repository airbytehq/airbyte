#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .sheet import SmartSheetAPIWrapper
from .streams import SmartsheetReportStream, SmartsheetStream


class SourceSmartsheets(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        sheet = SmartSheetAPIWrapper(config)
        return sheet.check_connection(logger)

    def streams(self, config: Mapping[str, Any]) -> List["Stream"]:
        sheet = SmartSheetAPIWrapper(config)
        if sheet.is_report:
            return [SmartsheetReportStream(sheet, config)]
        return [SmartsheetStream(sheet, config)]

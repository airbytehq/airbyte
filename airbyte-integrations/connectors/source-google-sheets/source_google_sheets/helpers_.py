#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import logging
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, FrozenSet, Iterable, List, Tuple

from airbyte_cdk.models.airbyte_protocol import AirbyteRecordMessage, AirbyteStream, ConfiguredAirbyteCatalog, SyncMode
from google.oauth2 import credentials as client_account
from google.oauth2 import service_account
from googleapiclient import discovery

from .models.spreadsheet import RowData, Spreadsheet
from .utils import safe_name_conversion

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive.readonly"]

logger = logging.getLogger("airbyte")


class Helpers(object):
    @staticmethod
    def get_sheets_to_column_index_to_name(first_row: List, names_conversion: bool = False) -> Dict[int, str]:
        # todo: probably I should remove the sheet_id from the dictionary is redundant
        sheets_to_column_index_to_name = {}
        if names_conversion:
            first_row = [safe_name_conversion(h) for h in first_row]
            # When performing names conversion, they won't match what is listed in catalog for the majority of cases,
            # so they should be cast here in order to have them in records
            # columns = {safe_name_conversion(c) for c in columns}
        # Find the column index of each header value
        idx = 0
        for cell_value in first_row:
            # if cell_value in columns:
            sheets_to_column_index_to_name[idx] = cell_value
            idx += 1
        return sheets_to_column_index_to_name

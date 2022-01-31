#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, Tuple, Union

import requests

class NGPVANClient:

    def __init__(self, van_api_key: str = None):
        self.van_api_key = van_api_key

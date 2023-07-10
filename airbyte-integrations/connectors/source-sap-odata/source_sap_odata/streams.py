#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import ctypes
import math
import os
import time
import urllib.parse
from abc import ABC
from contextlib import closing
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Type, Union

import pandas as pd
import pendulum
import requests  # type: ignore[import]
from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.core import Stream, StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from numpy import nan
from pendulum import DateTime  # type: ignore[attr-defined]
from requests import codes, exceptions

from .api import UNSUPPORTED_FILTERING_STREAMS, Salesforce
from .availability_strategy import SalesforceAvailabilityStrategy
from .exceptions import SalesforceException, TmpFileIOError
from .rate_limiting import default_backoff_handler

# https://stackoverflow.com/a/54517228
CSV_FIELD_SIZE_LIMIT = int(ctypes.c_ulong(-1).value // 2)
csv.field_size_limit(CSV_FIELD_SIZE_LIMIT)

DEFAULT_ENCODING = "utf-8"


class SalesforceStream(HttpStream, ABC):
    page_size = 2000
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    encoding = DEFAULT_ENCODING
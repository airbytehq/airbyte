from abc import ABC
from datetime import date, datetime, timedelta
from json import JSONDecodeError
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream



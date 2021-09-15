#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    Annotations,
    Cohorts,
    Events,
    EventsSessions,
    FeatureFlags,
    Insights,
    InsightsPath,
    InsightsSessions,
    Persons,
    PingMe,
    Trends,
)

DEFAULT_BASE_URL = "https://app.posthog.com"


class SourcePosthog(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            _ = pendulum.parse(config["start_date"])
            authenticator = TokenAuthenticator(token=config["api_key"])
            base_url = config.get("base_url", DEFAULT_BASE_URL)

            stream = PingMe(authenticator=authenticator, base_url=base_url)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            _ = next(records)
            return True, None
        except Exception as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == requests.codes.UNAUTHORIZED:
                return False, f"Please check you api_key. Error: {repr(e)}"
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        event/sessions stream is dynamic. Probably, it contains a list of CURRENT sessions.
        In Next day session may expire and wont be available via this endpoint.
        So we need a dynamic load data before tests.
        This stream was requested to be removed due to this reason.
        """
        authenticator = TokenAuthenticator(token=config["api_key"])
        base_url = config.get("base_url", DEFAULT_BASE_URL)

        return [
            Annotations(authenticator=authenticator, start_date=config["start_date"], base_url=base_url),
            Cohorts(authenticator=authenticator, base_url=base_url),
            Events(authenticator=authenticator, start_date=config["start_date"], base_url=base_url),
            EventsSessions(authenticator=authenticator, base_url=base_url),
            FeatureFlags(authenticator=authenticator, base_url=base_url),
            Insights(authenticator=authenticator, base_url=base_url),
            InsightsPath(authenticator=authenticator, base_url=base_url),
            InsightsSessions(authenticator=authenticator, base_url=base_url),
            Persons(authenticator=authenticator, base_url=base_url),
            Trends(authenticator=authenticator, base_url=base_url),
        ]

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

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    Blocks,
    Bounces,
    Campaigns,
    Contacts,
    GlobalSuppressions,
    InvalidEmails,
    Lists,
    Scopes,
    Segments,
    SingleSends,
    SpamReports,
    StatsAutomations,
    SuppressionGroupMembers,
    SuppressionGroups,
    Templates,
)


class SourceSendgrid(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = TokenAuthenticator(config["apikey"])
            scopes_gen = Scopes(authenticator=authenticator).read_records(sync_mode=SyncMode.full_refresh)
            next(scopes_gen)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Sendgrid API with the provided credentials - {error}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(config["apikey"])

        streams = [
            Lists(authenticator=authenticator),
            Campaigns(authenticator=authenticator),
            Contacts(authenticator=authenticator),
            StatsAutomations(authenticator=authenticator),
            Segments(authenticator=authenticator),
            SingleSends(authenticator=authenticator),
            Templates(authenticator=authenticator),
            GlobalSuppressions(authenticator=authenticator, start_time=config["start_time"]),
            SuppressionGroups(authenticator=authenticator),
            SuppressionGroupMembers(authenticator=authenticator),
            Blocks(authenticator=authenticator, start_time=config["start_time"]),
            Bounces(authenticator=authenticator, start_time=config["start_time"]),
            InvalidEmails(authenticator=authenticator, start_time=config["start_time"]),
            SpamReports(authenticator=authenticator, start_time=config["start_time"]),
        ]

        return streams

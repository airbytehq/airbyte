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


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .api import (
    Campaigns,
    Channels,
    EmailBounce,
    EmailClick,
    EmailComplaint,
    EmailOpen,
    EmailSend,
    EmailSendSkip,
    EmailSubscribe,
    EmailUnsubscribe,
    Lists,
    ListUsers,
    MessageTypes,
    Metadata,
    Templates,
    Users,
)


class SourceIterable(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            list(Lists(api_key=config["api_key"])._list_records(stream_state={}))
            return True, None
        except Exception as e:
            return False, f"Unable to connect to Iterable API with the provided credentials - {e}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        lists = Lists(api_key=config["api_key"])
        return [
            Campaigns(api_key=config["api_key"]),
            Channels(api_key=config["api_key"]),
            EmailBounce(api_key=config["api_key"], start_date=config["start_date"]),
            EmailClick(api_key=config["api_key"], start_date=config["start_date"]),
            EmailComplaint(api_key=config["api_key"], start_date=config["start_date"]),
            EmailOpen(api_key=config["api_key"], start_date=config["start_date"]),
            EmailSend(api_key=config["api_key"], start_date=config["start_date"]),
            EmailSendSkip(api_key=config["api_key"], start_date=config["start_date"]),
            EmailSubscribe(api_key=config["api_key"], start_date=config["start_date"]),
            EmailUnsubscribe(api_key=config["api_key"], start_date=config["start_date"]),
            lists,
            ListUsers(api_key=config["api_key"], parent_stream=lists),
            MessageTypes(api_key=config["api_key"]),
            Metadata(api_key=config["api_key"]),
            Templates(api_key=config["api_key"], start_date=config["start_date"]),
            Users(api_key=config["api_key"], start_date=config["start_date"]),
        ]

"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any, List, Mapping, Tuple

from base_python import AbstractSource, Stream

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
from .auth import ParamsAuthenticator


class SourceIterable(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = ParamsAuthenticator(config["api_key"])
            list(Lists(authenticator=authenticator)._list_records(stream_state={}))
            return True, None
        except Exception as e:
            return False, f"Unable to connect to Iterable API with the provided credentials - {e}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = ParamsAuthenticator(config["api_key"])

        lists = Lists(authenticator=authenticator)
        return [
            Campaigns(authenticator=authenticator),
            Channels(authenticator=authenticator),
            EmailBounce(start_date=config["start_date"], authenticator=authenticator),
            EmailClick(start_date=config["start_date"], authenticator=authenticator),
            EmailComplaint(start_date=config["start_date"], authenticator=authenticator),
            EmailOpen(start_date=config["start_date"], authenticator=authenticator),
            EmailSend(start_date=config["start_date"], authenticator=authenticator),
            EmailSendSkip(start_date=config["start_date"], authenticator=authenticator),
            EmailSubscribe(start_date=config["start_date"], authenticator=authenticator),
            EmailUnsubscribe(start_date=config["start_date"], authenticator=authenticator),
            lists,
            ListUsers(authenticator=authenticator, parent_stream=lists),
            MessageTypes(authenticator=authenticator),
            Metadata(authenticator=authenticator),
            Templates(start_date=config["start_date"], authenticator=authenticator),
            Users(start_date=config["start_date"], authenticator=authenticator),
        ]

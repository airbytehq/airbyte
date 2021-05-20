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

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .api import Addresses, Charges, Collections, Customers, Discounts, Metafields, Onetimes, Orders, Products, Shop, Subscriptions


class RechargeTokenAuthenticator(TokenAuthenticator):
    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Recharge-Access-Token": self._token}


class SourceRecharge(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            auth = RechargeTokenAuthenticator(token=config["access_token"])
            list(Shop(authenticator=auth).read_records(SyncMode.full_refresh))
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Recharge API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = RechargeTokenAuthenticator(token=config["access_token"])
        return [
            Addresses(authenticator=auth, start_date=config["start_date"]),
            Charges(authenticator=auth, start_date=config["start_date"]),
            Collections(authenticator=auth),
            Customers(authenticator=auth, start_date=config["start_date"]),
            Discounts(authenticator=auth, start_date=config["start_date"]),
            Metafields(authenticator=auth),
            Onetimes(authenticator=auth, start_date=config["start_date"]),
            Orders(authenticator=auth, start_date=config["start_date"]),
            Products(authenticator=auth),
            Shop(authenticator=auth),
            Subscriptions(authenticator=auth, start_date=config["start_date"]),
        ]

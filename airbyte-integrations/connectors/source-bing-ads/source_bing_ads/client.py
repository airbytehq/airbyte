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

from typing import Any, Mapping

from bingads.authorization import AuthorizationData, OAuthWebAuthCodeGrant
from bingads.service_client import ServiceClient
from suds.sudsobject import asdict


class Client:
    api_version: int = 13

    def __init__(
        self, developer_token: str, account_id: str, customer_id: str, client_secret: str, client_id: str, refresh_token: str, user_id: str
    ) -> None:
        self.authentication = OAuthWebAuthCodeGrant(
            client_id,
            client_secret,
            "",
        )

        self.authentication.request_oauth_tokens_by_refresh_token(refresh_token)

        self.authorization_data = AuthorizationData(
            account_id=account_id,
            customer_id=customer_id,
            developer_token=developer_token,
            authentication=self.authentication,
        )

    def get_service(self, serivce_name: str = "CustomerManagementService") -> ServiceClient:
        return ServiceClient(
            service=serivce_name,
            version=self.api_version,
            authorization_data=self.authorization_data,
            environment="production",
        )

    def set_elements_to_none(self, suds_object):
        # Bing Ads Campaign Management service operations require that if you specify a non-primitive,
        # it must be one of the values defined by the service i.e. it cannot be a nil element.
        # Since SUDS requires non-primitives and Bing Ads won't accept nil elements in place of an enum value,
        # you must either set the non-primitives or they must be set to None. Also in case new properties are added
        # in a future service release, it is a good practice to set each element of the SUDS object to None as a baseline.

        for element in suds_object:
            suds_object.__setitem__(element[0], None)
        return suds_object

    def recursive_asdict(self, d) -> Mapping[str, Any]:
        """
        Converts Suds object into serializable format.
        """
        out = {}

        for k, v in asdict(d).items():
            if hasattr(v, "__keylist__"):
                out[k] = self.recursive_asdict(v)
            elif isinstance(v, list):
                out[k] = []
                for item in v:
                    if hasattr(item, "__keylist__"):
                        out[k].append(self.recursive_asdict(item))
                    else:
                        out[k].append(item)
            else:
                out[k] = v
        return out

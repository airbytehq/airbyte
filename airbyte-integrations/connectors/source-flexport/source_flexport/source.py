#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_flexport.streams import Companies, FlexportError, FlexportStream, Invoices, Locations, Products, Shipments


class SourceFlexport(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        headers = {"Authorization": f"Bearer {config['api_key']}"}
        response = requests.get(f"{FlexportStream.url_base}network/companies?page=1&per=1", headers=headers)

        try:
            response.raise_for_status()
        except Exception as exc:
            try:
                error = response.json()["errors"][0]
                if error:
                    return False, FlexportError(f"{error['code']}: {error['message']}")
                return False, exc
            except Exception:
                return False, exc

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["api_key"])
        return [
            Companies(authenticator=auth),
            Locations(authenticator=auth),
            Products(authenticator=auth),
            Invoices(authenticator=auth),
            Shipments(authenticator=auth, start_date=config["start_date"]),
        ]

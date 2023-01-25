#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from source_qonto.auth import QontoApiKeyAuthenticator
from source_qonto.endpoint import get_url_base


# Basic full refresh stream
class QontoStream(HttpStream, ABC):
    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level.

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.
    """

    next_page_token_field = "current_page"
    primary_key = "id"

    def __init__(self, config: dict, stream_name: str, **kwargs):
        auth = QontoApiKeyAuthenticator(organization_slug=config["organization_slug"], secret_key=config["secret_key"])
        super().__init__(authenticator=auth, **kwargs)
        self.stream_name = stream_name
        self.config = config

    @property
    def url_base(self) -> str:
        return get_url_base(self.config["endpoint"])

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return self.stream_name

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Define how a response is parsed.
        :return an iterable containing each record in the response
        """
        response_json = response.json()
        yield from response_json[self.stream_name]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Define a pagination strategy.

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        decoded_response = response.json()
        api_metadata = decoded_response.get("meta", None)
        if api_metadata is None:
            return None
        else:
            next_page = api_metadata.get("next_page", None)
            if next_page is None:
                return None
            else:
                return {"current_page": next_page}


class Memberships(QontoStream):
    name = "memberships"

    def __init__(self, config, **kwargs):
        super().__init__(config, self.name)


class Labels(QontoStream):
    name = "labels"

    def __init__(self, config, **kwargs):
        super().__init__(config, self.name)


class Transactions(QontoStream):
    name = "transactions"
    cursor_date_format = "%Y-%m-%d"

    def __init__(self, config, **kwargs):
        super().__init__(config, self.name)
        self.start_date = config["start_date"]
        self.iban = config["iban"]

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """
        Define any query parameters to be set.
        """
        start_date = datetime.strptime(stream_state.get(self.cursor_field) if stream_state else self.start_date, self.cursor_date_format)
        params = {"iban": self.iban, "settled_at_from": start_date.strftime(self.cursor_date_format)}
        if next_page_token:
            params.update(next_page_token)
        return params


# Source
class SourceQonto(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            headers = {"Authorization": f'{config["organization_slug"]}:{config["secret_key"]}'}
            params = {"iban": config["iban"]}
            resp = requests.request("GET", url=f"{get_url_base(config['endpoint'])}/transactions", params=params, headers=headers)
            status = resp.status_code
            logger.info(f"Ping response code: {status}")
            if status == 200:
                return True, None
            if status == 404:
                if resp.text == " ":  # When Iban is wrong, the request returns only " " as content
                    message = "Not Found, the specified IBAN might be wrong"
                else:
                    message = resp.json().get("errors")[0].get("detail")
                return False, message
            if status == 401:
                message = "Invalid credentials, the organization slug or secret key might be wrong"
                return False, message
            return False, message
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Return a the list of streams that will be enabled in the connector

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [Memberships(config), Transactions(config), Labels(config)]

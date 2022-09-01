#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple, Optional
from urllib.parse import urlparse, parse_qs

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from requests.auth import HTTPBasicAuth

from source_klarna.schema_applier import SchemaApplier


class KlarnaStream(HttpStream, ABC):

    def __init__(self, authenticator: HTTPBasicAuth = None, region: str = 'eu', playground: bool = False,
                 ark_salt: str = '', **kwargs):
        self.playground: bool = playground
        self.region: str = region
        self.salt: bytes = ark_salt.encode()
        self.schema_applier = SchemaApplier(self.salt)
        super().__init__(authenticator=authenticator)

    page_size = 500

    @property
    def url_base(self) -> str:
        playground_path = 'playground.' if self.playground else ''
        if self.region == 'eu':
            endpoint = f"https://api.{playground_path}klarna.com/"
        else:
            endpoint = f"https://api-{self.region}.{playground_path}klarna.com/"
        return endpoint

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        if 'pagination' in response_json:
            if 'next' in response_json['pagination']:
                parsed_url = urlparse(response_json['pagination']['next'])
                query_params = parse_qs(parsed_url.query)
                # noinspection PyTypeChecker
                return query_params
        else:
            return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Usually contains common params e.g. pagination size etc.
        """
        if next_page_token:
            return dict(next_page_token)
        else:
            return {"offset": 0, "size": self.page_size}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield {}


class Transactions(KlarnaStream):
    primary_key = ["customer_id"]
    use_cache = True

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/settlements/v1/transactions"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        transactions = response.json().get("transactions", [])
        purchase_only_transactions = (
            self.schema_applier.apply_schema_transformations(t, self.get_json_schema())
            for t
            in transactions if
            ('detailed_type' in t and t['detailed_type'] == 'PURCHASE'))
        yield from purchase_only_transactions


class Orders(HttpSubStream, KlarnaStream):
    primary_key = "order_id"
    raise_on_http_errors = False

    def __init__(self, **kwargs):
        super().__init__(Transactions(**kwargs), **kwargs)

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
             next_page_token: Mapping[str, Any] = None
             ) -> str:
        order_id = stream_slice['parent']['order_id']
        return f"/ordermanagement/v1/orders/{order_id}"

    def __is_missing_orders(self, response: requests.Response) -> bool:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            response_json = response.json()
            if 'error_code' in response_json and response_json.get('error_code') == 'NO_SUCH_ORDER':
                self.logger.info(response.text)
                return True
            else:
                self.logger.error(response.text)
                raise exc

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if not self.__is_missing_orders(response):
            response_json = response.json()
            new_obj = self.schema_applier.apply_schema_transformations(response_json, self.get_json_schema())
            yield new_obj


# Basic incremental stream
class IncrementalKlarnaStream(KlarnaStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
            Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class SourceKlarna(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            auth = HTTPBasicAuth(username=config['username'], password=config['password'])
            conn_test_stream = Transactions(authenticator=auth, **config)
            conn_test_stream.page_size = 1
            conn_test_stream.next_page_token = lambda x: None
            records = conn_test_stream.read_records(sync_mode=SyncMode.full_refresh)
            # Try to read one value from records iterator
            next(records, None)
            return True, None
        except Exception as e:
            print(e)
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = HTTPBasicAuth(username=config['username'], password=config['password'])
        return [
            Transactions(authenticator=auth, **config),
            Orders(authenticator=auth, **config)
        ]


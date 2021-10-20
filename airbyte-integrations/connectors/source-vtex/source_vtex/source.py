#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import datetime
from airbyte_cdk.sources.streams.http import auth
from airbyte_cdk.sources.streams.http.http import HttpSubStream
import requests
from requests.api import head
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""


class VtexAuthenticator(requests.auth.AuthBase):
    def __init__(self, client_name, app_key, app_token):
        self.app_key = app_key
        self.app_token = app_token
        self.client_name = client_name

    def __call__(self, r):
        r.headers['x-vtex-api-appkey'] = self.app_key
        r.headers['x-vtex-api-apptoken'] = self.app_token

        return r

DATE_MASK = '%Y-%m-%dT%H:%M:%S.000Z'
FROM_VTEX_DATE_MASK = '%Y-%m-%dT%H:%M:%S.0000000+00:00'

class VtexStream(HttpStream, ABC):

    @property
    def url_base(self) -> str:
        client_name = self._session.auth.client_name
        return f"https://{client_name}.vtexcommercestable.com.br"

    def __init__(self, start_date: datetime, **kwargs):
        super().__init__(authenticator=kwargs['authenticator'])
        self.start_date = start_date

    def check_connection(self):
        start_date = datetime.datetime.now().strftime(DATE_MASK)
        orders_endpoint = '/api/oms/pvt/orders'

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        params = {
            'f_creationDate': f'creationDate:[{start_date} TO {start_date}]',
            'page': 1
        }

        url = self.url_base + orders_endpoint
        resp = requests.get(url, params=params, headers=headers, auth=self._session.auth)

        if resp.status_code != 200:
            return False, resp.content

        return True, None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        page = response_json['paging']['currentPage']
        totalPages = response_json['paging']['pages']

        if page <= totalPages:
            return { "page": page + 1 }

        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        start_date = self.start_date

        # VTEX seems to work with utc time
        end_date = (datetime.datetime.now() + datetime.timedelta(hours=3)) \
            .strftime('%Y-%m-%dT%H:%M:%S.000Z')

        if stream_state and self.cursor_field in stream_state:
            start_date = stream_state[self.cursor_field]

        page = next_page_token['page'] if next_page_token else 1

        return {
            'f_creationDate': f'creationDate:[{start_date} TO {end_date}]',
            'page': page
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()['list']


class IncrementalVtexStream(VtexStream, ABC):

    state_checkpoint_interval = None

    def __init__(self, lookback_window_days: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.lookback_window_days = lookback_window_days

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return 'creationDate'

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        if current_stream_state is not None and self.cursor_field in current_stream_state:
            current_date = current_stream_state[self.cursor_field]
            current_parsed_date = datetime.datetime.strptime(current_date, DATE_MASK)
            
            latest_record_date = latest_record.get(self.cursor_field)
            latest_record_parsed_date = datetime.datetime.strptime(latest_record_date, FROM_VTEX_DATE_MASK)
            
            return {self.cursor_field: max(current_parsed_date, latest_record_parsed_date).strftime(DATE_MASK)}
        else:
            return {self.cursor_field: self.start_date}


class Orders(IncrementalVtexStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """
    primary_key = "orderId"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return '/api/oms/pvt/orders'
        


class OrderDetails(HttpSubStream):
    ## Not sure how to do this
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """
    primary_key = "orderId"
    parent: object = Orders


    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        order_id = stream_slice["order_id"]
        return f'/api/oms/pvt/orders/{order_id}',


# Source
class SourceVtex(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        app_key = config['app_key']
        app_token = config['app_token']
        client_name = config['client_name']

        authenticator = VtexAuthenticator(
            client_name, app_key, app_token
        )

        stream = Orders(
            authenticator=authenticator
        )

        return stream.check_connection()

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        app_key = config['app_key']
        app_token = config['app_token']
        client_name = config['client_name']
        start_date = config['start_date']

        authenticator = VtexAuthenticator(
            client_name, app_key, app_token
        )

        return [
            Orders(authenticator=authenticator, start_date=start_date),
            OrderDetails(authenticator=authenticator, start_date=start_date)
        ]

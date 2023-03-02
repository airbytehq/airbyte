from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


__all__ = [
    'ProjectSyncStream',
    'IncrementalProjectSyncStream',
    'FinanceStream',
    'StaffTrackStream'
]


# Basic full refresh stream
class ProjectSyncStream(HttpStream, ABC):
    """
    TODO remove this comment

    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class ProjectSyncStream(HttpStream, ABC)` which is the current class
    `class Customers(ProjectSyncStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(ProjectSyncStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalProjectSyncStream((ProjectSyncStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    # TODO: Fill in the url base. Required.
    url_base = "https://example-api.com/v1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield {}


# Basic incremental stream
class IncrementalProjectSyncStream(ProjectSyncStream, ABC):
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

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class FinanceStream(HttpStream):
    url_base = "https://www.xledger.net/Flex/"

    primary_key = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "112706017670337.json?t=APLF6qr6AIDformleE2ylIO4JVobFhEOOgwYrhOsczHeskNkyONT6VkddFwDUnNtkB6aPnxsSjB_Nxf5mh5vfdvyQ2P6tp2jzobDJTFkWVYR__NFcHG8I1eeKjKiTiVg9wed3_licUXTOAAskDomtJ10XVsZ4Y_wGgPGtdsh5HMltyLaBPtoqiq0soyOWhQ4WFOTCNjPb2MV_qRrEF7waksPdydnNxiP4gDYWHFTnjwTYrHg7L_YDJy5BtvfJpqRg6_G8SE38F1GXG5LxZZVcZXhBqyqorDssO77b02pYr202OZWW_gB7ZsuDyLAYgC20wNdwJL2NZrGTUKLs18v"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        for row in response.json().get('rows'):
            yield {
                'Prosjekt #': row[0],
                'Prosjektnavn': row[1],
                'Hovedprosjekt': row[2],
                'Prosjekt-ID': row[3],
                'Firma/Person': row[4],
                'Prosjektgruppe': row[5],
                'Prosjektleder': row[6],
                'Fra': row[7],
                'Til': row[8],
                'Kontraktsbeløp': row[9],
                'Kostnad totalt': row[10],
                'Tot. est. timer': row[11],
                'Estimert dekningsgrad': row[12],
                'Koststed': row[13]
            }


class StaffTrackStream(HttpStream):
    url_base = "https://www.xledger.net/Flex/"

    primary_key = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "112706021316758.json?t=APLF6mVnpZ6Nsgmrcemx1NkG5rszx064kMTXhY3bzGQ8Haw38LgMcJxB0wI3BvfPEgE6dzw6efnleXPBGzjeahQRzLfTMtqXt8Tg8auDvVK5-N16fFGJ3raqFm8Y2Bi887qWKaApkPW0fnnXsQ0Uo8AhDKZFURKVlvoxREn1WD1qgLOiXXEivsOR0B2fo_y-zQKDYBuNUi817W-_iBmeeQBcASW89q_QTfq6ABvweVDpBmlfYj85JMGfQbWmQsEf_AgaSqZHBD3ns2IMo3_703MYG_2SMqiGlYgCBdI2Zo-NtUaVZ1YjF6EgLJHbVsZ-aBc01i5lGdPliQev8mGZ"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        for row in response.json().get('rows'):
            yield {
                'Prosjekt #': row[0],
                'Oppdrag': row[1],
                'Oppgave': row[2],
                'Periode': row[3],
                'Ansatt': row[4],
                'Stilling': row[5],
                'Plan': row[6],
                'Timer': row[7],
                'Allokert': row[8],
                'Planlagt': row[9],
            }

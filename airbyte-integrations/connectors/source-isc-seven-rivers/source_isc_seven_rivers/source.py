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
import datetime
from abc import ABC
from operator import itemgetter
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
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


# Basic full refresh stream
class IscSevenRiversStream(HttpStream, ABC):
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
    `class IscSevenRiversStream(HttpStream, ABC)` which is the current class
    `class Customers(IscSevenRiversStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(IscSevenRiversStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalIscSevenRiversStream((IscSevenRiversStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    # TODO: Fill in the url base. Required.
    url_base = "https://nmisc-wf.gladata.com/api/"

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
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
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

        yield from response.json()['data']


class MonitoringPoints(IscSevenRiversStream):
    """
    """

    cursor_field = "id"

    primary_key = "id"

    def path(self, **kwargs) -> str:
        """
        return "single". Required.
        """
        return "getMonitoringPoints.ashx"


class Analytes(IscSevenRiversStream):
    cursor_field = "id"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        """
        return "single". Required.
        """
        return "getAnalytes.ashx"


class Observations(IscSevenRiversStream):
    _active_page = None

    def __init__(self, *args, **kw):
        super(Observations, self).__init__(*args, **kw)
        p = MonitoringPoints()
        records = list(p.read_records('full-refresh'))
        self._pages = (r for r in sorted(r['id'] for r in records))

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        if not next_page_token:
            next_page_token = next(self._pages)

        self._active_page = next_page_token
        td = datetime.timedelta(days=1)
        params = {'id': next_page_token,
                  'start': 0,
                  'end': int((datetime.datetime.now() - td).timestamp() * 1000)}

        self._request_params_hook(params)
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        try:
            r = next(self._pages)
            return r
        except StopIteration:
            pass

    def _request_params_hook(self, params):
        pass


class WaterLevels(Observations):
    cursor_field = "id"
    primary_key = "id"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        records = response.json()['data']
        if records:
            for r in records:
                r['monitoring_point_id'] = self._active_page
            yield from records

    def path(self, **kwargs) -> str:
        """
        return "single". Required.
        """
        return "getWaterLevels.ashx"


class Readings(Observations):
    cursor_field = "id"
    primary_key = "id"

    def __init__(self, *args, **kw):
        super(Readings, self).__init__(*args, **kw)
        p = MonitoringPoints()
        ps = list(p.read_records('full-refresh'))

        a = Analytes()
        ans = list(a.read_records('full-refresh'))

        self._pages = ((pi['id'], ai['id']) for pi in sorted(ps, key=itemgetter('id'))
                       for ai in sorted(ans, key=itemgetter('id')))

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        records = response.json()['data'] or []
        if records:
            for r in records:
                r['monitoring_point_id'] = self._active_page[0]
                r['analyte_id'] = self._active_page[1]
            yield from records

    def _request_params_hook(self, params):
        params['analyteid'] = params['id'][1]
        params['monitoringPointId'] = params['id'][0]
        del params['id']

    def path(self, **kwargs) -> str:
        """
        return "single". Required.
        """
        return "getReadings.ashx"


# Source
class SourceIscSevenRivers(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        auth = TokenAuthenticator(token="api_key")  # Oauth2Authenticator is also available if you need oauth support
        return [
            MonitoringPoints(authenticator=auth),
            Analytes(authenticator=auth),
            WaterLevels(authenticator=auth),
            Readings(authenticator=auth)
        ]

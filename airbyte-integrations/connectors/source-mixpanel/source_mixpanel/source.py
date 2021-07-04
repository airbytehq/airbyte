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


import base64

from abc import ABC
from datetime import date, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from urllib.parse import parse_qs, urlparse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator, TokenAuthenticator
from airbyte_cdk.logger import AirbyteLogger

class MixpanelStream(HttpStream, ABC):

    url_base = "https://mixpanel.com/api/2.0/"
    date_window_size = 30  # days

    def __init__(
        self,
        authenticator: HttpAuthenticator,
        start_date: Union[date, str] = None,
        end_date: Union[date, str] = None,
        date_window_size: int = 30,  # in days
        **kwargs,
    ):
        self.date_window_size = date_window_size

        super().__init__(authenticator=authenticator)

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

    def date_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        date_slices = []

        # use the latest date between self.start_date and stream_state
        start_date = max(self.start_date, date.fromisoformat(stream_state["date"]) if stream_state else self.start_date)
        # use the lowest date between start_date and self.end_date, otherwise API fails if start_date is in future
        start_date = min(start_date, self.end_date)

        while start_date <= self.end_date:
            end_date = start_date + timedelta(days=self.date_window_size)
            date_slices.append(
                {
                    "start_date": str(start_date),
                    "end_date": str(min(end_date, self.end_date)),
                }
            )
            # add 1 additional day because date range is inclusive
            start_date = end_date + timedelta(days=1)

        print(f"==== date_slices: {date_slices} \n")
        return date_slices

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

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
        json_response = response.json()
        if self.data_field is not None:
            data = json_response.get(self.data_field, [])
        elif isinstance(json_response, list):
            data = json_response
        elif isinstance(json_response, dict):
            data = [json_response]

        print(f"Total data: {len(data)}")

        for record in data:
            # sleep(3)
            yield record


class IncrementalMixpanelStream(MixpanelStream, ABC):

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        # This method is called once for each record returned from the API to compare the cursor field value in that record with the current state
        # we then return an updated state object. If this is the first time we run a sync or no state was passed, current_stream_state will be None.
        current_stream_state = current_stream_state or {}
        current_stream_state_date = current_stream_state.get("date", str(self.start_date))
        latest_record_date = latest_record.get(self.cursor_field, str(self.start_date))
        return {"date": max(current_stream_state_date, latest_record_date)}


class FunnelsList(MixpanelStream):
    """API Docs: https://developer.mixpanel.com/reference/funnels#funnels-list-saved

    endpoint = https://mixpanel.com/api/2.0/funnels/list
    """

    primary_key = "funnel_id"
    data_field = None

    def path(self, **kwargs) -> str:
        return "funnels/list"


class Funnels(IncrementalMixpanelStream):
    """List the funnels for a given date range.
    API Docs: https://developer.mixpanel.com/reference/funnels#funnels-query

    endpoint = "https://mixpanel.com/api/2.0/funnels"
    """

    primary_key = ["funnel_id", "date"]
    data_field = "data"
    cursor_field = "date"

    def path(self, **kwargs) -> str:
        return "funnels"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        # print(f"stream_slice: f{stream_slice} \n")
        return {
            "funnel_id": stream_slice["funnel_id"],
            # 'unit': 'day'
            "from_date": stream_slice["start_date"],
            "to_date": stream_slice["end_date"],
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        response.json() example:
        {
            "meta": {
                "dates": [
                    "2016-09-12"
                    "2016-09-19"
                    "2016-09-26"
                ]
            }
            "data": {
                "2016-09-12": {
                    "steps": [...]
                    "analysis": {
                        "completion": 20524
                        "starting_amount": 32688
                        "steps": 2
                        "worst": 1
                    }
                }
                "2016-09-19": {
                    ...
                }
            }
        }
        :return an iterable containing each record in the response
        """
        # extract 'funnel_id' from internal request object
        query = urlparse(response.request.path_url).query
        params = parse_qs(query)
        funnel_id = int(params["funnel_id"][0])

        records = response.json().get(self.data_field, {})
        for date_entry in records:
            # for each record add funnel_id, name
            yield {
                "funnel_id": funnel_id,
                "name": self.funnels[funnel_id],
                "date": date_entry,
                **records[date_entry],
            }

    def funnel_slices(self, sync_mode) -> List[dict]:

        funnel_slices = FunnelsList(authenticator=self.authenticator).read_records(sync_mode=sync_mode)
        funnel_slices = list(funnel_slices)  # [{'funnel_id': <funnel_id1>, 'name': <name1>}, {...}]
        print(f"==== funnel_slices: {funnel_slices} \n")

        # save all funnels in dict(<funnel_id1>:<name1>, ...)
        self.funnels = dict((funnel["funnel_id"], funnel["name"]) for funnel in funnel_slices)

        return funnel_slices

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        :param stream_state:
        :return:
        """

        print(f"==== stream_state: {stream_state}")

        # One stream slice is a combination of all funnel_slices and stream_slices
        stream_slices = []
        funnel_slices = self.funnel_slices(sync_mode)
        date_slices = self.date_slices(sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        for funnel_slice in funnel_slices:
            for date_slice in date_slices:
                stream_slices.append({**funnel_slice, **date_slice})

        print(f"==== stream_slices: {stream_slices} \n")
        return stream_slices


class Cohorts(MixpanelStream):
    """Returns all of the cohorts in a given project.
    API Doc: https://developer.mixpanel.com/reference/cohorts

    endpoint: https://mixpanel.com/api/2.0/cohorts/list

    [{
        "count": 150
        "is_visible": 1
        "description": "This cohort is visible, has an id = 1000, and currently has 150 users."
        "created": "2019-03-19 23:49:51"
        "project_id": 1
        "id": 1000
        "name": "Cohort One"
    },
    {
        "count": 25
        "is_visible": 0
        "description": "This cohort isn't visible, has an id = 2000, and currently has 25 users."
        "created": "2019-04-02 23:22:01"
        "project_id": 1
        "id": 2000
        "name": "Cohort Two"
    }
    ]

    """

    data_field = None
    primary_key = "id"
    cursor_field = "created"

    def path(self, **kwargs) -> str:
        return "cohorts/list"


class Engage(MixpanelStream):
    """Return list of all users

    API Doc: https://developer.mixpanel.com/reference/engage

    Endpoint: https://mixpanel.com/api/2.0/engage

    {
        "page": 0
        "page_size": 1000
        "session_id": "1234567890-EXAMPL"
        "status": "ok"
        "total": 1
        "results": [{
            "$distinct_id": "9d35cd7f-3f06-4549-91bf-198ee58bb58a"
            "$properties":{
                "$browser":"Chrome"
                "$browser_version":"83.0.4103.116"
                "$city":"Leeds"
                "$country_code":"GB"
                "$region":"Leeds"
                "$timezone":"Europe/London"
                "unblocked":"true"
                "$email":"nadine@asw.com"
                "$first_name":"Nadine"
                "$last_name":"Burzler"
                "$name":"Nadine Burzler"
                "id":"632540fa-d1af-4535-bc52-e331955d363e"
                "$last_seen":"2020-06-28T12:12:31"
                }
            },{
            ...
            }
        ]

    }
    """
    http_method = "POST"
    data_field = "results"
    primary_key = "distinct_id"
    page_size = 1000  # min 100
    _total = None

    def path(self, **kwargs) -> str:
        return "engage"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return {"include_all_users": True}
        # return {'filter_by_cohort': '{"id":1343181}'}
        # return {'filter_by_cohort': {"id": 1343181}}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"page_size": self.page_size}
        if next_page_token:
            params.update(next_page_token)
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Override this method to define a pagination strategy.

        The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.

        :return: The token for the next page from the input response object. Returning None means there are no more pages to read in this response.
        """
        decoded_response = response.json()
        page_number = decoded_response.get("page")
        total = decoded_response.get("total")  # exist only on first page
        if total:
            self._total = total

        if self._total and page_number is not None and self._total > self.page_size * (page_number + 1):
            return {
                "session_id": decoded_response.get("session_id"),
                "page": page_number + 1,
            }
        else:
            self._total = None
            return None


class CohortMembers(Engage):
    """Return list of users grouped by cohort"""

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:

        id = stream_slice["id"]
        # ss= f'{{"id":"{d["id"]}"}}'
        ss = f'{{"id":{id}}}'
        jj = {"filter_by_cohort": ss}
        print(jj)
        print()
        # example: {"filter_by_cohort": {"id": 1343181}}
        return {"filter_by_cohort": stream_slice}

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        :param stream_state:
        :return:
        """
        stream_slices = []
        cohorts = Cohorts(authenticator=self.authenticator).read_records(sync_mode=sync_mode)
        for cohort in cohorts:
            stream_slices.append({"id": cohort["id"]})

        print(f"==== stream_slices: {stream_slices} \n")

        # stream_slices = [{"id": 1343181}]
        return stream_slices


class Annotations(MixpanelStream):
    """List the annotations for a given date range.
    API Docs: https://developer.mixpanel.com/reference/annotations
    endpoint: "https://mixpanel.com/api/2.0/annotations

    Output example:
    {
        "annotations": [{
                "id": 640999
                "project_id": 2117889
                "date": "2021-06-16 00:00:00" <-- PLEASE READ NOTE
                "description": "Looks good"
            }, {...}
        ]
    }

    NOTE: annotation date - is the date for which annotation was added, this is not the date when annotation was added
    That's why stream does not support incremental sync.
    """

    data_field = "annotations"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "annotations"

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        :param stream_state:
        :return:
        """
        return self.date_slices(sync_mode, cursor_field=cursor_field, stream_state=stream_state)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "from_date": stream_slice["start_date"],
            "to_date": stream_slice["end_date"],
        }


class Revenue(IncrementalMixpanelStream):
    """Get data from your Insights reports.
    API Docs: https://developer.mixpanel.com/reference/insights
    Endpoint: https://mixpanel.com/api/2.0/insights
    """

    data_field = "results"
    primary_key = "date"
    cursor_field = "date"

    def path(self, **kwargs) -> str:
        return "engage/revenue"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "from_date": stream_slice["start_date"],
            "to_date": stream_slice["end_date"],
        }

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        :param stream_state:
        :return:
        """
        return self.date_slices(sync_mode, cursor_field=cursor_field, stream_state=stream_state)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        response.json() example:
        {
            'computed_at': '2021-07-03T12:43:48.889421+00:00',
            'results': {
                '$overall': {       <-- should be skipped?
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                '2021-06-01': {
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                '2021-06-02': {
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                ...
            },
            'session_id': '162...',
            'status': 'ok'
        }
        :return an iterable containing each record in the response
        """
        records = response.json().get(self.data_field, {})
        for date_entry in records:
            yield {"date": date_entry, **records[date_entry]}


class Export(MixpanelStream):
    """Export event data as it is received and stored within Mixpanel, complete with all event properties
     (including distinct_id) and the exact timestamp the event was fired.

    API Docs: https://developer.mixpanel.com/reference/export
    Endpoint: https://data.mixpanel.com/api/2.0/export


    url = "https://data.mixpanel.com/api/2.0/export"

    querystring = {"from_date":"2021-01-01","to_date":"2021-07-01"}

    headers = {
        "Accept": "application/json",
        "Authorization": "Basic ZGVhNTE4ZDQ0YmYzNWE0ZjBmZDBlMmFhM2QxMTVhNjE6"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)


     Your plan does not support raw data export. Visit mixpanel.com/pricing to upgrade.

    [
    {
        "event":"Viewed report"
        "properties": {
            "time": 1518393599
            "distinct_id": "test-email@mixpanel.com"
            "$browser": "Chrome"
            "report_name": "Funnels"
        }
    }
    ]

    """
    data_field = None
    primary_key = 'time'
    cursor_field = 'time'

    def path(self, **kwargs) -> str:
        return "export"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "from_date": stream_slice["start_date"],
            "to_date": stream_slice["end_date"],
        }

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        :param stream_state:
        :return:
        """
        return self.date_slices(sync_mode, cursor_field=cursor_field, stream_state=stream_state)

class TokenAuthenticatorBase64(TokenAuthenticator):
    def __init__(self, token: str, auth_method: str = "Basic", **kwargs):
        token = base64.b64encode(token.encode("utf8")).decode("utf8")
        super().__init__(token=token, auth_method=auth_method, **kwargs)


class SourceMixpanel(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        authenticator = TokenAuthenticatorBase64(token=config["api_secret"])
        try:
            response = requests.request(
                "GET",
                url="https://mixpanel.com/api/2.0/funnels/list",
                headers={
                    "Accept": "application/json",
                    **authenticator.get_auth_header(),
                },
            )

            if response.status_code != 200:
                message = response.json()
                error_message = message.get("error")
                if error_message:
                    return False, error_message
                response.raise_for_status()
        except Exception as e:
            return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        now = date.today()

        start_date = config.get('start_date')
        if start_date and isinstance(start_date, str):
            start_date = date.fromisoformat(config['start_date'])
        config['start_date'] = start_date or now - timedelta(days=365)  # set to 1 year ago by default

        end_date = config.get('start_date')
        if end_date and isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
        config['end_date'] = end_date or now  # set to now by default

        AirbyteLogger().log("INFO", f"Using start_date: {config['start_date']}, end_date: {config['end_date']}")

        auth = TokenAuthenticatorBase64(token=config["api_secret"])
        return [
            Funnels(authenticator=auth, **config),
            Engage(authenticator=auth, **config),
            Cohorts(authenticator=auth, **config),
            CohortMembers(authenticator=auth, **config),
            Annotations(authenticator=auth, **config),
            Revenue(authenticator=auth, **config),
        ]

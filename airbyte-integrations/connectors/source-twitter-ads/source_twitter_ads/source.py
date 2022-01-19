#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
 
import requests
from requests_oauthlib import OAuth1

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
class TwitterAdsStream(HttpStream, ABC):
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
    `class TwitterAdsStream(HttpStream, ABC)` which is the current class
    `class Customers(TwitterAdsStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(TwitterAdsStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalTwitterAdsStream((TwitterAdsStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

        # TODO: Fill in the url base. Required.
    url_base = "https://ads-api.twitter.com/"
    primary_key = None

    def __init__(self, base,  account_id,  authenticator,  start_time, end_time, granularity, metric_groups, placement, **kwargs):
        super().__init__(authenticator, **kwargs)
        self.account_id = account_id
        self.auth = authenticator
        self.start_time = start_time
        self.end_time = end_time
        self.granularity = granularity
        self.metric_groups = metric_groups
        self.placement = placement

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

        # twitter ads analytics streams don't offer pagination => we return None.
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """

        account_id = self.account_id
        auth = self.auth
        # FixMe: request returns a bad request error if (end_time - start_time)> 7 this could lead to problems
        start_time = self.start_time
        end_time = self.end_time
        granularity = self.granularity
        metric_groups = self.metric_groups
        placement = self.placement
        campaign_ids_url = "https://ads-api.twitter.com/10/accounts/" + account_id + "/campaigns"
        response = requests.get(campaign_ids_url, auth=auth)
        campaign_ids = []

        for each in response.json()['data']:
            campaign_ids.append(each["id"])

        campaign_ids = list(set(campaign_ids))

    
        return { "entity": "CAMPAIGN", "entity_ids": campaign_ids, "start_time":start_time, "end_time": end_time,"granularity": granularity, "placement": placement, "metric_groups": metric_groups}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        # fix me parse response
        return [response.json()]


class Campaigns(TwitterAdsStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        # fixme: account id should not be hardcoded
        account_id = self.account_id
        return "/10/stats/accounts/" + account_id


# Basic incremental stream
class IncrementalTwitterAdsStream(TwitterAdsStream, ABC):
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

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        TODO: Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

        Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
        This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
        section of the docs for more information.

        The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
        necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
        This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

        An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
        craft that specific request.

        For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
        this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
        till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
        the date query param.
        """
        raise NotImplementedError("Implement stream slices or delete this method!")


# Source
class SourceTwitterAds(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        url = 'https://ads-api.twitter.com/10/accounts'
        auth = OAuth1(config["CONSUMER_KEY"], config["CONSUMER_SECRET"], config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"])
        check_connection_respone = (requests.get(url, auth=auth))

        if check_connection_respone.status_code ==  200:
            return True, None
        else:
            return False,  "Unable to connect to Twitter Ads API with the provided credentials"
             
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        auth = OAuth1(config["CONSUMER_KEY"], config["CONSUMER_SECRET"], config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"])  # Oauth2Authenticator is also available if you need oauth support
        return [Campaigns(base="https://ads-api.twitter.com/", authenticator=auth, account_id = config["ACCOUNT_ID"] , start_time = config["START_TIME"], end_time = config["END_TIME"], granularity = config["GRANULARITY"], metric_groups = config["METRIC_GROUPS"], placement = config["PLACEMENT"])] 

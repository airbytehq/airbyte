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
import urllib
import json
import datetime
import gzip
from io import BytesIO
import time
import logging


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

    def __init__(self, base,  account_id,  authenticator,  start_time, granularity, metric_groups, placement, segmentation, **kwargs):
        super().__init__(authenticator, **kwargs)
        self.account_id = account_id
        self.auth = authenticator
        self.start_time = start_time
        self.granularity = granularity
        self.metric_groups = metric_groups
        self.placement = placement
        self.segmentation = segmentation

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

    
        next_page_token = response.json()['next_cursor']
        return next_page_token
    

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        return {"cursor": next_page_token}
     

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """

        if self.__class__.__name__ == "AdsAnalyticsMetrics":
            job_urls = self.job_urls
            results = []

            for job_url in job_urls:
                with requests.get(job_url) as zipped_result:
                 json_bytes = gzip.open(BytesIO(zipped_result.content)).read()

                json_str = json_bytes.decode('utf-8') 
                results_full = dict(json.loads(json_str))

                result_data = results_full.get("data")
                result_params = results_full.get("request")

                for item in result_data:
                    item['params'] = result_params.get('params')

                results.append(result_data)



            results =[ item for sublist in results for item in sublist]

            return results
        else:
            response_json = response.json()
            result = response_json.get("data")

            return result
        




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
        auth = self.auth
        account_id = self.account_id

        request_url = "https://ads-api.twitter.com/10/accounts/" + account_id + "/campaigns?count=1000"
        
        return request_url

class LineItems(TwitterAdsStream):
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
        auth = self.auth
        account_id = self.account_id

        request_url = "https://ads-api.twitter.com/10/accounts/" + account_id + "/line_items?count=1000"
        
        return request_url

class PromotedTweets(TwitterAdsStream):
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
        account_id = self.account_id

        request_url = "https://ads-api.twitter.com/10/accounts/" + account_id + "/promoted_tweets?count=1000"
        
        return request_url

class AdsAnalyticsMetrics(TwitterAdsStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        
        auth = self.auth
        #ToDo: we need to specifiy a start/end time different from the one in the config as maximum time span is 45days for this endpoint, think about what we want/need here + make it as part of config?
        start_time = str((datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"))
        end_time = str(datetime.date.today().strftime("%Y-%m-%d"))
        granularity = self.granularity
        metric_groups =  self.metric_groups
        account_id = self.account_id
        placements = self.placement
        segmentation = self.segmentation
        entity = "PROMOTED_TWEET"
        
        # getting activie promoted tweet ids
        promoted_tweet_ids_url = "https://ads-api.twitter.com/9/stats/accounts/" + account_id + "/active_entities?"
        promoted_tweet_ids_params = urllib.parse.urlencode({"start_time": start_time, "end_time": end_time, "entity": entity})
        promoted_tweet_ids_params = urllib.parse.unquote(promoted_tweet_ids_params)
        promoted_tweet_ids_url = promoted_tweet_ids_url + promoted_tweet_ids_params
        response = requests.get(promoted_tweet_ids_url, auth=auth)
        promoted_tweet_ids = []

        for each in response.json()['data']:
            promoted_tweet_ids.append(each["entity_id"])

 
        promoted_tweet_ids = list(set(promoted_tweet_ids))


        # This twitter ads api endpoint allows only 20 entity ids per request
        # Therefore we are splitting entity ids in list with len < 20 and loop through the lists
        promoted_tweet_ids = [promoted_tweet_ids[i * 20:(i + 1) * 20 ] for i in range((len(promoted_tweet_ids) + 20 - 1) // 20)]

        promoted_tweet_ids_str = []
        for each in promoted_tweet_ids:
            each = ','.join(each)
            promoted_tweet_ids_str.append(each)


        metric_groups = ','.join(metric_groups)

        job_urls = []
        job_success_urls = [] 
        job_statuses = []

        # we need to do seperate requests for different placements. We might want to do this in seperate streams instead of Looping
        for placement in placements:

            for each in promoted_tweet_ids_str:
                post_base_url = "https://ads-api.twitter.com/10/stats/jobs/accounts/" + account_id + '?'
                params_post =  urllib.parse.urlencode({"start_time": start_time, "end_time": end_time, "entity": entity, "entity_ids": each, "granularity": "DAY", "placement": placement, "metric_groups": metric_groups, "segmentation_type": segmentation})
                params_post =  urllib.parse.unquote(params_post)
                post_url = post_base_url + params_post
                post_response = requests.post(post_url,  auth=auth)
                post_response = post_response.json()

                try:
                    job_id = post_response['data']['id_str']
                except KeyError:
                    logging.error("Post Response:")
                    loggin.error(response.json())
                    logging.error("Check Source Configuration")

                job_success_url = "https://ads-api.twitter.com/10/stats/jobs/accounts/" + account_id + "?"
                job_success_params = urllib.parse.urlencode({"job_id": job_id})
                job_success_params = urllib.parse.unquote(job_success_params)
                job_success_url = job_success_url + job_success_params
            
                job_success_response = requests.get(job_success_url, auth=auth)
                job_success_response = job_success_response.json()
                job_status = job_success_response['data'][0]['status']
                job_url = job_success_response['data'][0]['url']
                
                job_urls.append(job_url)
                job_success_urls.append(job_success_url)
                job_statuses.append(job_status)

            for job_success_url,job_status in zip(job_success_urls, job_statuses):
                # ToDo: What happens if job fails? 
                while job_status != "SUCCESS":
                    time.sleep(30)
                    job_success_response = requests.get(job_success_url, auth=auth)
                    job_success_response = job_success_response.json()
                    job_status = job_success_response['data'][0]['status']
                    job_url = job_success_response['data'][0]['url']
                
                    job_urls.append(job_url)


            
        # dropping none values from job_urls
        job_urls = [url for url in job_urls if url]
        self.job_urls = job_urls

        request_url =  job_success_url

        return request_url

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
        return [Campaigns(base="https://ads-api.twitter.com/", authenticator=auth, account_id = config["ACCOUNT_ID"] , start_time = config["START_TIME"], granularity = config["GRANULARITY"], metric_groups = config["METRIC_GROUPS"], placement = config["PLACEMENT"], segmentation = config["SEGMENTATION"]),
        LineItems(base="https://ads-api.twitter.com/", authenticator=auth,account_id = config["ACCOUNT_ID"] , start_time = config["START_TIME"], granularity = config["GRANULARITY"], metric_groups = config["METRIC_GROUPS"], placement = config["PLACEMENT"], segmentation = config["SEGMENTATION"]),
        PromotedTweets(base="https://ads-api.twitter.com/", authenticator=auth,account_id = config["ACCOUNT_ID"] , start_time = config["START_TIME"], granularity = config["GRANULARITY"], metric_groups = config["METRIC_GROUPS"], placement = config["PLACEMENT"], segmentation = config["SEGMENTATION"]),
        AdsAnalyticsMetrics(base="https://ads-api.twitter.com/", authenticator=auth, account_id = config["ACCOUNT_ID"] , start_time = config["START_TIME"],granularity = config["GRANULARITY"], metric_groups = config["METRIC_GROUPS"], placement = config["PLACEMENT"], segmentation = config["SEGMENTATION"])]

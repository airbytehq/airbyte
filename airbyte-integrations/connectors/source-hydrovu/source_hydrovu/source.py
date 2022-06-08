#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator, Oauth2Authenticator
#from airbyte_cdk.sources.streams import IncrementalMixin
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from datetime import datetime
import json

"""
Source connector for HydroVu API
"""

# Basic full refresh stream
class HydroVuStream(HttpStream, ABC):
    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class HydrovuStream(HttpStream, ABC)` which is the current class
    `class Customers(HydrovuStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(HydrovuStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalHydrovuStream((HydrovuStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    # Required url_base for hydrovu api
    url_base = "https://www.hydrovu.com/public-api/v1/"

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


class FriendlyNames(HydroVuStream):
    """
    Gets friendly names parameters and units from HydroVu API
    """

    # Required
    primary_key = "id"
    
    def __init__(self, *args, **kw):
        super(FriendlyNames, self).__init__(*args, **kw)


    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        End of URL path to locations list from API
        """
        return "sispec/friendlynames"
    

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        The X-ISI-Start-Page is a header that is required if accessing any page beyond the fist
        page from the given path to the locations list. If accessing the first page, then the
        header can be empty.
        """

        # If there is a next_page_token from the previous page of the list of locations,
        # then set the X-ISI-Start-Page header.
        if next_page_token:
            return {"X-ISI-Start-Page": next_page_token}
            
        else:
            return {}


    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        If there is a next page listed in the response header, then the string for that 
        page will be parsed.
        """

        try:
            r = response.headers['X-ISI-Next-Page']
            return r

        except:
            pass

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parses the response of friendly names. 
        """

        yield response.json()


class Locations(HydroVuStream):
    """
    Gets list of locations from HydroVu API
    """

    # Required
    primary_key = "id"
    
    def __init__(self, *args, **kw):
        super(Locations, self).__init__(*args, **kw)


    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        End of URL path to locations list from API
        """
        return "locations/list"
    

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        The X-ISI-Start-Page is a header that is required if accessing any page beyond the fist
        page from the given path to the locations list. If accessing the first page, then the
        header can be empty.
        """

        # If there is a next_page_token from the previous page of the list of locations,
        # then set the X-ISI-Start-Page header.
        if next_page_token:
            return {"X-ISI-Start-Page": next_page_token}
            
        else:
            return {}


    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        If there is a next page listed in the response header, then the string for that 
        page will be parsed.
        """

        try:
            r = response.headers['X-ISI-Next-Page']
            return r

        except:
            pass


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parses the response of locations list to create records and associated parameters 
        for each location.  
        """

        def format_record(r):

            gps = r['gps']
            del r['gps']
            r['latitude'] = gps['latitude']
            r['longitude'] = gps['longitude']
            return r

        yield from (format_record(r) for r in response.json())


class Readings(HydroVuStream):
    """
    Gets readings for each location from HydroVu API
    """

    # Required
    primary_key = 'id'

    cursor_field = "latest_timestamp_for_each_location"

    def __init__(self, auth, *args, **kw):
        super(Readings, self).__init__(*args, **kw)

        # Call Locations class in order to get the list of locations
        locations = Locations(authenticator=auth)

        records = list(locations.read_records('full-refresh'))

        # Create _pages iterable storing each location id
        self._pages = (location for location in sorted(location['id'] for location in records))

        self._cursor_value = None

        # Dictionary to store the latest timestamp read in for each location throughout
        # the reading process
        self.location_latest_timestamps = {} 

        # Dictionary to store the timestamp for each location read in from the stored 
        # state at the beginning of the reading process 
        self.state_location_timestamps = {} 

        # Boolean to indicate to move on to the next location reading
        self.continue_to_next_location_reading = False

        self.next_location_page = ""


    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        End of URL path to location date from API
        """

        # If next_page_token is empty, then iterate to next location page
        if not next_page_token:
            self.next_location_page = next(self._pages)

        # Else if the second element of the next_page_token tuple contains a location id,
        # then set the next location page to that location id.
        elif len(str(next_page_token[1])) > 0:
            self.next_location_page = next_page_token[1]

        return f"locations/{self.next_location_page}/data"


    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        The X-ISI-Start-Page is a header that is required if accessing any page beyond the fist
        page from the given path to the readings for a given location. If accessing the first page, then the
        header can be empty.
        """

        # If the next_page_token exists and if the first element of the next_page_token
        # tuple is not empty, then the X-ISI-Start-Page header to the string in that element. 
        if next_page_token and len(next_page_token[0]) > 0:
            return {"X-ISI-Start-Page": next_page_token[0]}
            
        else:
            return {}


    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        The startTime parameter is required if wanting to pull data starting at any other time 
        than the first Epoch timestamp available from the API. This is set up to stored state as the 
        last timestamp read for each location. Therefore, when Airbyte executes a new run with these
        timestamps stored in state, the timestamps will be read in from state and set as the startTime
        parameter to read data from that timestamp until the most recently available timestamp.
        """
      
        # Check to see if self.location_latest_timestamps is an empty dictionary.
        # It is only empty on the first overall call of a given run to request_params.
        # If this is the first time Airbyte is run, and no state is stored, then these
        # will remain as empty dictionaries.
        if not bool(self.location_latest_timestamps):

            # This dictionary will be continously be updated throughout a run
            self.location_latest_timestamps = stream_state
       
            # Dictionary copy makes a shallow copy of the dictionary.
            # This dictionary will remain static throughout a run and only contain the
            # state that is read in at the beginning. If there is no state available to
            # be read in, then this dictionary will remain empty for the run.
            self.state_location_timestamps = self.location_latest_timestamps.copy()

        # If there are timestamps from state for a given location, then set that to startTime.
        # Otherwise, params will be empty.
        try:
            params = {'startTime': self.state_location_timestamps[str(self.next_location_page)]}

        except:
            params = {}

        return params


    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        '''
        If no X-ISI-Next-Page, then the next page token will be the next of self._pages to iterate
        over the location ids.  
        '''

        isi_next_page = ""

        next_location_page = ""

        # If the readings response for a given location has a next page, then set that to isi_next_page
        # and return it in a tuple.
        try:
            isi_next_page = response.headers['X-ISI-Next-Page']

            return (isi_next_page, next_location_page)

        except:

            # Otherwise, if there is another location id to continue to, then iterate to the next
            # of self._pages to retrieve that location id and return that in a tuple with the 
            # isi_next_page as an empty string.
            try:
                next_location_page = next(self._pages)

                return (isi_next_page, next_location_page)

            # Otherwise, there are no more pages for a given location's reading adn there are no
            # more location ids to iterate.
            except StopIteration:
                pass


    @property
    def state(self) -> Mapping[str, Any]:
        '''
        Saves self.location_latest_timestamps to state to be store between Airbyte runs.
        '''

        return self.location_latest_timestamps


    @state.setter
    def state(self, value: Mapping[str, Any]):
        '''
        Sets the stream state from the stored state after the stream is initialized.
        '''
        self._cursor_value = self.cursor_field


    def update_state(self):
        '''
        Original update state method but not currently used. Leave in here in case needed in future.
        Sends an update of the state variable to stdout.
        '''
        output_message = {"type":"STATE","state":{"data":self.location_latest_timestamps}}
        
        print(json.dumps(output_message))


    def parse_response(self, 
        response: requests.Response, 
        stream_state: Mapping[str, Any],
        **kwargs) -> Iterable[Mapping]:
        """
        Parses the response of a given reading for a location to create records and associated parameters.  
        """

        response_json = response.json() 

        r = response.json()

        flat_readings_list = []
        
        locationId = r['locationId']

        parameters = r['parameters']

        # If there is a latest timestamp from a previous run or a previous call to this function
        # for this location, then set cursor_timestamp to that value.
        try:
            cursor_timestamp = self.location_latest_timestamps[str(locationId)]
        except:
            cursor_timestamp = 0

        for param in parameters:

            parameterId = param['parameterId']

            unitId = param['unitId']

            customParameter = param['customParameter']

            readings = param['readings']

            previous_timestamp = 0

            for reading in readings:

                timestamp = reading['timestamp']

                if timestamp > cursor_timestamp:

                    time_utc_iso = datetime.utcfromtimestamp(timestamp).isoformat()

                    value = reading['value']

                    flat_reading = {}

                    flat_reading['locationId'] = locationId
                    flat_reading['parameterId'] = parameterId
                    flat_reading['unitId'] = unitId
                    flat_reading['customParameter'] = customParameter
                    flat_reading['timestamp'] = timestamp
                    flat_reading['time_utc_iso'] = time_utc_iso
                    flat_reading['value'] = value

                    flat_readings_list.append(flat_reading)

        # Sets to latest timestamp to save to state
        self.location_latest_timestamps[str(locationId)] = timestamp

        yield from flat_readings_list


class myOauth2Authenticator(Oauth2Authenticator):

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        Returns a tuple of (access_token, token_lifespan_in_seconds)
        """
        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        response_json = oauth.fetch_token(token_url=self.token_refresh_endpoint,
                                          client_id=self.client_id,
                                          client_secret=self.client_secret)
        return response_json[self.access_token_name], response_json[self.expires_in_name]


# Source
class SourceHydrovu(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Implements a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            # create session
            auth = myOauth2Authenticator(
                                     config['token_refresh_endpoint'],
                                     config['client_id'],
                                     config['client_secret'],
                                     ""
                                     )
            return True, None

        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        auth = myOauth2Authenticator(
                                     config['token_refresh_endpoint'],
                                     config['client_id'],
                                     config['client_secret'],
                                     ""
                                     )

        return [FriendlyNames(authenticator=auth), Locations(authenticator=auth), Readings(auth, authenticator=auth)]

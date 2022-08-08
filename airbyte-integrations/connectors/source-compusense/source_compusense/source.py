#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator,HttpAuthenticator
from airbyte_cdk.sources.streams.http.requests_native_auth.token import BasicHttpAuthenticator
from airbyte_cdk.sources.streams import IncrementalMixin

# Basic full refresh stream
class CompusenseStream(HttpStream, ABC):
    """
    """

    url_base = "https://plentytestdataapi.compusensecloud.com/jf6testresultsapife/api/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        """
        # TODO (kbochanski@plenty.ag): These should be dynamic
        return {"start":"20220101","end":"20220710"}
    
    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        # TODO (kbochanski@plenty.ag): Determine why exactyl this is required for Compusense API
        return {'user-agent': "airbyte-client"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        # Since Compusense data is of the type array, return type does not need to be wrapped with []
        return response.json()


class SurveyMetadata(CompusenseStream):
    """
    """

    primary_key = "testId"

    def __init__(self, **kwargs):
        # Pass authenticator to parent class
        super().__init__(**kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        """
        # Appends return value to base url
        return "testmetadata"


# Basic incremental stream
class IncrementalCompusenseStream(CompusenseStream, ABC):
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


class Employees(IncrementalCompusenseStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the cursor_field. Required.
    cursor_field = "start_date"

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "employee_id"

    def path(self, **kwargs) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
        return "single". Required.
        """
        return "employees"

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
class SourceCompusense(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        # TODO (kbochanski@plenty.ag): May want to use TokenAuthenticator?
        auth = requests.auth.HTTPBasicAuth(config["client_id"],config["client_secret"])
        url = "https://plentytestdataapi.compusensecloud.com/jf6testresultsapife/api/testmetadata"
        querystring = {"start":"20220101","end":"20220710"}
        headers = {
            'user-agent': "airbyte-client",
            }
        try:
            
            logger.info('Checking Compusense Connection...')
            # TODO (kbochanski@plenty.ag): Is a health endpoint to hit instead?
            response = requests.get(url, auth = auth, headers=headers, params=querystring)

            # Check that data is returned
            assert response.status_code == 200
            body = response.json()
            assert len(body) > 0
            
            return True, None
        except requests.exceptions.RequestException as e:
            logger(e)
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        client_id = config["client_id"]
        client_secret = config["client_secret"]
        # See https://github.com/airbytehq/airbyte/blob/94abef3acc085320a6493a557d6bcdd31252f94f/airbyte-cdk/python/airbyte_cdk/sources/streams/http/requests_native_auth/token.py
        auth = BasicHttpAuthenticator(client_id,client_secret)

        return [SurveyMetadata(authenticator=auth),]

# TODO (kbochanski@plenty.ag): Need to finish testing and docs - https://docs.airbyte.com/connector-development/tutorials/building-a-python-source
# TODO (kbochanski@plenty.ag): Will want to use an incremental loader BUT query only takes date inputs and data returned does not have a single date field (would need to combine day,month,year)

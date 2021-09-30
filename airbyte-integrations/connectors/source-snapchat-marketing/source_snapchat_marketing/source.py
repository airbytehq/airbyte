#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

# See the get_depend_on_ids function explanation
# Long story short - used as cache for ids of higher level streams, that is used
# as path variables in other streams. And to avoid requesting those ids for every stream
# we put them to a dict and check if they exist on stream calling
# The structure be like:
# {
#   'Organizations': [
#       {'organization_id': '7f064d90-52a1-some-uuid'}
#   ],
#   'Adaccounts': [
#       {'ad_account_id': '04214c00-3aa5-some-uuid'},
#       {'ad_account_id': 'e4cd371b-8de8-some-uuid'}
#   ]
# }
#
auxiliary_id_map = {}

# The default value that is returned by stream_slices if there is no slice found: [None]
default_stream_slices_return_value = [None]


class SnapchatMarketingException(Exception):
    """ Just for formatting the exception as SnapchatMarketing"""


def get_depend_on_ids(depends_on_stream, depends_on_stream_config: Mapping, slice_key_name: str) -> List:
    """This auxiliary function is to help retrieving the ids from another stream

    :param depends_on_stream: The stream class from what we need to retrieve ids
    :param depends_on_stream_config: parameters for depends_on_stream class
    :param slice_key_name: The key in result slices generator
    :param logger: Logger to log the messages
    :returns: empty list in case no ids of the stream was found or list with {slice_key_name: id}
    """

    # The trick with this code is that some streams are chained:
    # For example Creatives -> AdAccounts -> Organizations.
    # Creatives need the ad_account_id as path variable
    # AdAccounts need the organization_id as path variable
    # So organization_ids from Organizations goes as slices to AdAccounts
    # and after that ad_account_ids from AdAccounts goes as slices to Creatives for path variables
    # So first we must get the AdAccounts, then do the slicing for them
    # and then call the read_records for each slice

    # If the depends_on_stream is None (which means class can be incremental but don't need any slicing with ids)
    # then just return default_stream_slices_return_value (which is [None])
    if depends_on_stream is None:
        return default_stream_slices_return_value

    # This auxiliary_id_map is used to prevent the extracting of ids that are used in most streams
    # Instead of running the request to get (for example) AdAccounts for each stream as slices we put them in the dict and
    # return if the same ids are requested in the stream. This saves us a lot of time and requests
    if depends_on_stream.__name__ in auxiliary_id_map:
        return auxiliary_id_map[depends_on_stream.__name__]

    # Some damn logic a?
    # Relax, that has some meaning:
    # if we want to get just 1 level of parent ids (For example AdAccounts need the organization_ids from Organizations, but
    # Organizations do not have slices and returns [None] from stream_slices method) this switch goes for else clause and get all the
    # organization_ids from Organizations and return them as slices
    # But in case we want to retrieve 2 levels of parent ids (For example we run Creatives stream - it needs the ad_account_ids from AdAccount
    # and AdAccount need organization_ids from Organizations and first we must get all organization_ids
    # and for each of them get the ad_account_ids) so switch goes to if claus to get all the nested ids.
    # Let me visualize this for you:
    #
    #           organization_id_1                      organization_id_2
    #                 / \                                    / \
    #                /   \                                  /   \
    # ad_account_id_1     ad_account_id_2    ad_account_id_3     ad_account_id_4
    #
    # So for the AdAccount slices will be [{'organization_id': organization_id_1}, {'organization_id': organization_id_2}]
    # And for the Creatives (Media, Ad, AdSquad, etc...) the slices will be
    # [{'ad_account_id': ad_account_id_1}, {'ad_account_id': ad_account_id_2},
    #  {'ad_account_id': ad_account_id_3},{'ad_account_id': ad_account_id_4}]
    #
    # After getting all the account_ids, they go as slices to Creatives (Media, Ad, AdSquad, etc...)
    # and are used in the path function as a path variables according to the API docs

    depend_on_stream = depends_on_stream(**depends_on_stream_config)
    depend_on_stream_slices = depend_on_stream.stream_slices(sync_mode=SyncMode.full_refresh)
    depend_on_stream_ids = []

    if depend_on_stream_slices != default_stream_slices_return_value:
        for depend_on_stream_slice in depend_on_stream_slices:
            records = depend_on_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=depend_on_stream_slice)
            depend_on_stream_ids += [{slice_key_name: record["id"]} for record in records]
    else:
        depend_on_stream_ids = [{slice_key_name: record["id"]} for record in depend_on_stream.read_records(sync_mode=SyncMode.full_refresh)]

    if not depend_on_stream_ids:
        return []

    auxiliary_id_map[depends_on_stream.__name__] = depend_on_stream_ids
    return depend_on_stream_ids


class SnapchatMarketingStream(HttpStream, ABC):
    url_base = "https://adsapi.snapchat.com/v1/"
    primary_key = "id"

    @property
    def response_root_name(self):
        """ Using the class name in lower to set the root node for response parsing """
        return self.name

    @property
    def response_item_name(self):
        """
        Used as the second level node for response parsing. Usually it is the response_root_name without last char.
        For example: response_root_name = organizations, so response_item_name = organization
        The [:-1] removes the last char from response_root_name: organizations -> organization
         {
            "organizations": [
                {
                    "organization": {....}
                }
            ]
        }
        """
        return self.response_root_name[:-1]

    def __init__(self, start_date, **kwargs):
        super().__init__(**kwargs)
        self.start_date = pendulum.parse(start_date).to_rfc3339_string()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page_cursor = response.json().get("paging", False)
        if next_page_cursor:
            return {"cursor": dict(parse_qsl(urlparse(next_page_cursor["next_link"]).query))["cursor"]}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token or {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """Response json came like
        {
            "organizations": [
                {
                    "organization": {
                        "id": "some uuid",
                        "updated_at": "2020-12-15T22:35:17.819Z",
                        "created_at": "2020-12-15T11:13:03.910Z",
                        ... some_other_json_fields ...
                    }
                }
            ]
        }
        So the response_root_name will be "organizations", and the response_item_name will be "organization"
        Also, the client side filtering for incremental sync is used
        """
        json_response = response.json().get(self.response_root_name)
        for resp in json_response:
            if self.response_item_name not in resp:
                error_text = f"JSON field named '{self.response_item_name}' is absent in the response for {self.name} stream"
                self.logger.error(error_text)
                raise SnapchatMarketingException(error_text)
            yield resp.get(self.response_item_name)


class IncrementalSnapchatMarketingStream(SnapchatMarketingStream, ABC):
    cursor_field = "updated_at"
    depends_on_stream = None
    slice_key_name = "ad_account_id"

    last_slice = None
    current_slice = None
    first_run = True
    initial_state = None
    max_state = None

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        stream_state = kwargs.get("stream_state")
        self.initial_state = stream_state.get(self.cursor_field) if stream_state else self.start_date
        self.max_state = self.initial_state
        depends_on_stream_config = {"authenticator": self.authenticator, "start_date": self.start_date}
        stream_slices = get_depend_on_ids(self.depends_on_stream, depends_on_stream_config, self.slice_key_name)

        if not stream_slices:
            self.logger.error(f"No {self.slice_key_name}s found. {self.name} cannot be extracted without {self.slice_key_name}.")
            yield from []

        self.last_slice = stream_slices[-1]
        yield from stream_slices

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        I see you have a lot of questions to this function. I will try to explain.
        The problem that it solves is next: records from the streams that used nested ids logic (see the get_depend_on_ids function comments below)
        can have different, non ordered timestamp in update_at cursor_field and because of they are extracted with slices
        it is a messy task to make the stream works as incremental. To understand it better the read of nested stream data can be next:

        # Reading the data subset for the ad_account_id_1 - first slice
        {"updated_at": "2021-07-22T10:32:05.719Z", other_fields}
        {"updated_at": "2021-07-22T10:47:05.780Z", other_fields}
        {"updated_at": "2021-07-22T10:42:03.830Z", other_fields}
        {"updated_at": "2021-07-21T12:20:34.927Z", other_fields}
        # Reading the data subset for the ad_account_id_2 - second slice
        {"updated_at": "2021-07-07T07:40:09.531Z", other_fields}
        {"updated_at": "2021-06-11T08:04:42.202Z", other_fields}
        {"updated_at": "2021-06-09T13:12:56.350Z", other_fields}

        As you can see the cursor_field (updated_at) values are not ordered and even more - they are descending in some kind
        The standard logic for incremental cannot be done, because in this case after the first slice
        the stream_state will be 2021-07-22T10:42:03.830Z, but the second slice data is less then this value, so it will not be yield

        So the next approach was implemented: Until the last slice is processed the stream state remains initial (whenever it is a start_date
        or the saved stream_state from the state.json), but the maximum value is calculated and saved in class max_state value.
        When the last slice is processed (we write the class last_slice value while getting the slices) the max_state value is written to stream_state
        Thus all the slices data are compared to the initial state, but only on the last one we write it to the stream state.
        This approach gives us the maximum state value of all the records and we exclude the state updates between slice processing
        """

        if self.first_run:
            self.first_run = False
            return {self.cursor_field: self.initial_state}
        else:
            self.max_state = max(self.max_state, latest_record[self.cursor_field])
            return {self.cursor_field: self.max_state if self.current_slice == self.last_slice else self.initial_state}

    def read_records(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        """
        This structure is used to set the class variable current_slice to the current stream slice for the
        purposes described above.
        Then all the retrieved records if the stream_state is present are filtered by the cursor_field value compared to the stream state
        This makes the incremental magic works
        """
        self.current_slice = stream_slice
        records = super().read_records(stream_slice=stream_slice, stream_state=stream_state, **kwargs)
        if stream_state:
            for record in records:
                if record[self.cursor_field] > stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"adaccounts/{stream_slice[self.slice_key_name]}/{self.response_root_name}"


class Organizations(SnapchatMarketingStream):
    """ Docs: https://marketingapi.snapchat.com/docs/#organizations """

    def path(self, **kwargs) -> str:
        return "me/organizations"


class Adaccounts(IncrementalSnapchatMarketingStream):
    """ Docs: https://marketingapi.snapchat.com/docs/#get-all-ad-accounts """

    depends_on_stream = Organizations
    slice_key_name = "organization_id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"organizations/{stream_slice[self.slice_key_name]}/adaccounts"


class Creatives(IncrementalSnapchatMarketingStream):
    """ Docs: https://marketingapi.snapchat.com/docs/#get-all-creatives """

    depends_on_stream = Adaccounts


class Media(IncrementalSnapchatMarketingStream):
    """ Docs: https://marketingapi.snapchat.com/docs/#get-all-media """

    depends_on_stream = Adaccounts

    @property
    def response_item_name(self):
        return self.response_root_name


class Campaigns(IncrementalSnapchatMarketingStream):
    """ Docs: https://marketingapi.snapchat.com/docs/#get-all-campaigns """

    depends_on_stream = Adaccounts


class Ads(IncrementalSnapchatMarketingStream):
    """ Docs: https://marketingapi.snapchat.com/docs/#get-all-ads-under-an-ad-account """

    depends_on_stream = Adaccounts


class Adsquads(IncrementalSnapchatMarketingStream):
    """ Docs: https://marketingapi.snapchat.com/docs/#get-all-ad-squads-under-an-ad-account """

    depends_on_stream = Adaccounts


class Segments(IncrementalSnapchatMarketingStream):
    """ Docs: https://marketingapi.snapchat.com/docs/#get-all-audience-segments """

    depends_on_stream = Adaccounts


class SnapchatAdsOauth2Authenticator(Oauth2Authenticator):
    """Request example for API token extraction:
    curl -X POST https://accounts.snapchat.com/login/oauth2/access_token \
      -d "refresh_token={refresh_token}" \
      -d "client_id={client_id}" \
      -d "client_secret={client_secret}"  \
      -d "grant_type=refresh_token"  \
    """

    def __init__(self, config):
        super().__init__(
            token_refresh_endpoint="https://accounts.snapchat.com/login/oauth2/access_token",
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )

    def refresh_access_token(self) -> Tuple[str, int]:
        response_json = None
        try:
            response = requests.request(method="POST", url=self.token_refresh_endpoint, data=self.get_refresh_request_body())
            response_json = response.json()
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if response_json and "error" in response_json:
                raise Exception(
                    "Error refreshing access token. Error: {}; Error details: {}; Exception: {}".format(
                        response_json["error"], response_json["error_description"], e
                    )
                ) from e
            raise Exception(f"Error refreshing access token: {e}") from e
        else:
            return response_json["access_token"], response_json["expires_in"]


# Source
class SourceSnapchatMarketing(AbstractSource):
    """Source Snapchat Marketing helps to retrieve the different Ad data from Snapchat business account"""

    def check_connection(self, logger, config) -> Tuple[bool, any]:

        try:
            auth = SnapchatAdsOauth2Authenticator(config)
            token = auth.get_access_token()
            url = f"{SnapchatMarketingStream.url_base}me"

            session = requests.get(url, headers={"Authorization": "Bearer {}".format(token)})
            session.raise_for_status()
            return True, None

        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = SnapchatAdsOauth2Authenticator(config)
        kwargs = {"authenticator": auth, "start_date": config["start_date"]}
        return [
            Adaccounts(**kwargs),
            Ads(**kwargs),
            Adsquads(**kwargs),
            Campaigns(**kwargs),
            Creatives(**kwargs),
            Media(**kwargs),
            Organizations(**kwargs),
            Segments(**kwargs),
        ]

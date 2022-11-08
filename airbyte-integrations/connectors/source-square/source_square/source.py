#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator
from requests.auth import AuthBase
from source_square.utils import separate_items_by_count


class SquareException(Exception):
    """Just for formatting the exception as Square"""

    def __init__(self, status_code, errors):
        self.status_code = status_code
        self.errors = errors

    def __str__(self):
        return f"Code: {self.status_code}, Detail: {self.errors}"


def parse_square_error_response(error: requests.exceptions.HTTPError) -> SquareException:
    if error.response.content:
        content = json.loads(error.response.content.decode())
        if content and "errors" in content:
            return SquareException(error.response.status_code, content["errors"])


class SquareStream(HttpStream, ABC):
    def __init__(
        self,
        is_sandbox: bool,
        api_version: str,
        start_date: str,
        include_deleted_objects: bool,
        authenticator: Union[AuthBase, HttpAuthenticator],
    ):
        super().__init__(authenticator)
        self._authenticator = authenticator
        self.is_sandbox = is_sandbox
        self.api_version = api_version
        # Converting users ISO 8601 format (YYYY-MM-DD) to RFC 3339 (2021-06-14T13:47:56.799Z)
        # Because this standard is used by square in 'updated_at' records field
        self.start_date = pendulum.parse(start_date).to_rfc3339_string()
        self.include_deleted_objects = include_deleted_objects

    data_field = None
    primary_key = "id"
    items_per_page_limit = 100

    @property
    def url_base(self) -> str:
        return "https://connect.squareup{}.com/v2/".format("sandbox" if self.is_sandbox else "")

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page_cursor = response.json().get("cursor", False)
        if next_page_cursor:
            return {"cursor": next_page_cursor}

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Square-Version": self.api_version, "Content-Type": "application/json"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.data_field, []) if self.data_field is not None else json_response
        yield from records

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        try:
            return super()._send_request(request, request_kwargs)
        except requests.exceptions.HTTPError as e:
            square_exception = parse_square_error_response(e)
            if square_exception:
                self.logger.error(str(square_exception))
            raise e


# Some streams require next_page_token in request query parameters (TeamMemberWages, Customers)
# but others in JSON payload (Items, Discounts, Orders, etc)
# That's why this 2 classes SquareStreamPageParam and SquareStreamPageJson are made
class SquareStreamPageParam(SquareStream, ABC):
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"cursor": next_page_token["cursor"]} if next_page_token else {}


class SquareStreamPageJson(SquareStream, ABC):
    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Mapping]:
        return {"cursor": next_page_token["cursor"]} if next_page_token else {}


class SquareStreamPageJsonAndLimit(SquareStreamPageJson, ABC):
    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Mapping]:
        json_payload = {"limit": self.items_per_page_limit}
        if next_page_token:
            json_payload.update(next_page_token)

        return json_payload


class SquareCatalogObjectsStream(SquareStreamPageJson):
    data_field = "objects"
    http_method = "POST"
    items_per_page_limit = 1000

    def path(self, **kwargs) -> str:
        return "catalog/search"

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Mapping]:
        json_payload = super().request_body_json(stream_state, stream_slice, next_page_token)

        if self.path() == "catalog/search":
            json_payload["include_deleted_objects"] = self.include_deleted_objects
            json_payload["include_related_objects"] = False
            json_payload["limit"] = self.items_per_page_limit

        return json_payload


class IncrementalSquareGenericStream(SquareStream, ABC):
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if current_stream_state is not None and self.cursor_field in current_stream_state:
            return {self.cursor_field: max(current_stream_state[self.cursor_field], latest_record[self.cursor_field])}
        else:
            return {self.cursor_field: self.start_date}


class IncrementalSquareCatalogObjectsStream(SquareCatalogObjectsStream, IncrementalSquareGenericStream, ABC):
    @property
    @abstractmethod
    def object_type(self):
        """Object type property"""

    state_checkpoint_interval = SquareCatalogObjectsStream.items_per_page_limit

    cursor_field = "updated_at"

    def request_body_json(self, stream_state: Mapping[str, Any], **kwargs) -> Optional[Mapping]:
        json_payload = super().request_body_json(stream_state, **kwargs)

        if stream_state:
            json_payload["begin_time"] = stream_state[self.cursor_field]

        json_payload["object_types"] = [self.object_type]
        return json_payload


class IncrementalSquareStream(IncrementalSquareGenericStream, SquareStreamPageParam, ABC):
    state_checkpoint_interval = SquareStream.items_per_page_limit

    cursor_field = "created_at"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params_payload = super().request_params(stream_state, stream_slice, next_page_token)

        if stream_state:
            params_payload["begin_time"] = stream_state[self.cursor_field]

        params_payload["limit"] = self.items_per_page_limit

        return params_payload


class Items(IncrementalSquareCatalogObjectsStream):
    """Docs: https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects
    with object_types = ITEM"""

    object_type = "ITEM"


class Categories(IncrementalSquareCatalogObjectsStream):
    """Docs: https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects
    with object_types = CATEGORY"""

    object_type = "CATEGORY"


class Discounts(IncrementalSquareCatalogObjectsStream):
    """Docs: https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects
    with object_types = DISCOUNT"""

    object_type = "DISCOUNT"


class Taxes(IncrementalSquareCatalogObjectsStream):
    """Docs: https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects
    with object_types = TAX"""

    object_type = "TAX"


class ModifierList(IncrementalSquareCatalogObjectsStream):
    """Docs: https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects
    with object_types = MODIFIER_LIST"""

    object_type = "MODIFIER_LIST"


class Refunds(IncrementalSquareStream):
    """Docs: https://developer.squareup.com/reference/square_2021-06-16/refunds-api/list-payment-refunds"""

    data_field = "refunds"

    def path(self, **kwargs) -> str:
        return "refunds"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params_payload = super().request_params(**kwargs)
        params_payload["sort_order"] = "ASC"

        return params_payload


class Payments(IncrementalSquareStream):
    """Docs: https://developer.squareup.com/reference/square_2021-06-16/payments-api/list-payments"""

    data_field = "payments"

    def path(self, **kwargs) -> str:
        return "payments"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params_payload = super().request_params(**kwargs)
        params_payload["sort_order"] = "ASC"

        return params_payload


class Locations(SquareStream):
    """Docs: https://developer.squareup.com/explorer/square/locations-api/list-locations"""

    data_field = "locations"

    def path(self, **kwargs) -> str:
        return "locations"


class Shifts(SquareStreamPageJsonAndLimit):
    """Docs: https://developer.squareup.com/reference/square/labor-api/search-shifts"""

    data_field = "shifts"
    http_method = "POST"
    items_per_page_limit = 200

    def path(self, **kwargs) -> str:
        return "labor/shifts/search"


class TeamMembers(SquareStreamPageJsonAndLimit):
    """Docs: https://developer.squareup.com/reference/square/team-api/search-team-members"""

    data_field = "team_members"
    http_method = "POST"

    def path(self, **kwargs) -> str:
        return "team-members/search"


class TeamMemberWages(SquareStreamPageParam):
    """Docs: https://developer.squareup.com/reference/square_2021-06-16/labor-api/list-team-member-wages"""

    data_field = "team_member_wages"
    items_per_page_limit = 200

    def path(self, **kwargs) -> str:
        return "labor/team-member-wages"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params_payload = super().request_params(**kwargs)
        params_payload = params_payload or {}

        params_payload["limit"] = self.items_per_page_limit
        return params_payload

    # This stream is tricky because once in a while it returns 404 error 'Not Found for url'.
    # Thus the retry strategy was implemented.
    def should_retry(self, response: requests.Response) -> bool:
        return response.status_code == 404 or super().should_retry(response)

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        return 3


class Customers(SquareStreamPageParam):
    """Docs: https://developer.squareup.com/reference/square_2021-06-16/customers-api/list-customers"""

    data_field = "customers"

    def path(self, **kwargs) -> str:
        return "customers"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params_payload = super().request_params(**kwargs)
        params_payload = params_payload or {}

        params_payload["sort_order"] = "ASC"
        params_payload["sort_field"] = "CREATED_AT"
        return params_payload


class Orders(SquareStreamPageJson):
    """Docs: https://developer.squareup.com/reference/square/orders-api/search-orders"""

    data_field = "orders"
    http_method = "POST"
    items_per_page_limit = 500
    # There is a restriction in the documentation where only 10 locations can be send at one request
    # https://developer.squareup.com/reference/square/orders-api/search-orders#request__property-location_ids
    locations_per_requets = 10

    def path(self, **kwargs) -> str:
        return "orders/search"

    def request_body_json(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Optional[Mapping]:
        json_payload = super().request_body_json(stream_slice=stream_slice, **kwargs)
        json_payload = json_payload or {}

        if stream_slice:
            json_payload.update(stream_slice)

        json_payload["limit"] = self.items_per_page_limit
        return json_payload

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        locations_stream = Locations(
            authenticator=self.authenticator,
            is_sandbox=self.is_sandbox,
            api_version=self.api_version,
            start_date=self.start_date,
            include_deleted_objects=self.include_deleted_objects,
        )
        locations_records = locations_stream.read_records(sync_mode=SyncMode.full_refresh)
        location_ids = [location["id"] for location in locations_records]

        if not location_ids:
            self.logger.error(
                "No locations found. Orders cannot be extracted without locations. "
                "Check https://developer.squareup.com/explorer/square/locations-api/list-locations"
            )
            yield from []

        separated_locations = separate_items_by_count(location_ids, self.locations_per_requets)
        for location in separated_locations:
            yield {"location_ids": location}


class Oauth2AuthenticatorSquare(Oauth2Authenticator):
    def refresh_access_token(self) -> Tuple[str, int]:
        """Handle differences in expiration attr:
        from API: "expires_at": "2021-11-05T14:26:57Z"
        expected: "expires_in": number of seconds
        """
        token, expires_at = super().refresh_access_token()
        expires_in = pendulum.parse(expires_at) - pendulum.now()
        return token, expires_in.seconds


class SourceSquare(AbstractSource):
    api_version = "2021-09-15"  # Latest Stable Release

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> AuthBase:

        credential = config.get("credentials", {})
        auth_type = credential.get("auth_type")
        if auth_type == "Oauth":
            # scopes needed for all currently supported streams:
            scopes = [
                "CUSTOMERS_READ",
                "EMPLOYEES_READ",
                "ITEMS_READ",
                "MERCHANT_PROFILE_READ",
                "ORDERS_READ",
                "PAYMENTS_READ",
                "TIMECARDS_READ",
                # OAuth Permissions:
                # https://developer.squareup.com/docs/oauth-api/square-permissions
                # https://developer.squareup.com/reference/square/enums/OAuthPermission
                # "DISPUTES_READ",
                # "GIFTCARDS_READ",
                # "INVENTORY_READ",
                # "INVOICES_READ",
                # "TIMECARDS_SETTINGS_READ",
                # "LOYALTY_READ",
                # "ONLINE_STORE_SITE_READ",
                # "ONLINE_STORE_SNIPPETS_READ",
                # "SUBSCRIPTIONS_READ",
            ]

            auth = Oauth2AuthenticatorSquare(
                token_refresh_endpoint="https://connect.squareup.com/oauth2/token",
                client_secret=credential.get("client_secret"),
                client_id=credential.get("client_id"),
                refresh_token=credential.get("refresh_token"),
                scopes=scopes,
                expires_in_name="expires_at",
            )
        elif auth_type == "Apikey":
            auth = TokenAuthenticator(token=credential.get("api_key"))
        elif not auth_type and config.get("api_key"):
            auth = TokenAuthenticator(token=config.get("api_key"))
        else:
            raise Exception(f"Invalid auth type: {auth_type}")

        return auth

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:

        headers = {
            "Square-Version": self.api_version,
            "Content-Type": "application/json",
        }
        auth = self.get_auth(config)
        headers.update(auth.get_auth_header())

        url = "https://connect.squareup{}.com/v2/catalog/info".format("sandbox" if config["is_sandbox"] else "")

        try:
            session = requests.get(url, headers=headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            square_exception = parse_square_error_response(e)
            if square_exception:
                return False, square_exception.errors[0]["detail"]

            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        args = {
            "authenticator": self.get_auth(config),
            "is_sandbox": config["is_sandbox"],
            "api_version": self.api_version,
            "start_date": config["start_date"],
            "include_deleted_objects": config["include_deleted_objects"],
        }
        return [
            Items(**args),
            Categories(**args),
            Discounts(**args),
            Taxes(**args),
            Locations(**args),
            TeamMembers(**args),
            TeamMemberWages(**args),
            Refunds(**args),
            Payments(**args),
            Customers(**args),
            ModifierList(**args),
            Shifts(**args),
            Orders(**args),
        ]

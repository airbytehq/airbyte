#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .auth import TrustpilotApikeyAuthenticator, TrustpilotOauth2Authenticator
from .streams import BusinessUnits, ConfiguredBusinessUnits, PrivateReviews


class SourceTrustpilot(AbstractSource):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.__public_auth_params: Mapping[str, Any] = {}
        self.__oauth2_auth_params: Mapping[str, Any] = {}
        self.__configured_business_units_stream: Optional[ConfiguredBusinessUnits] = None

    def _public_auth_params(self, config: MutableMapping[str, Any]):
        """
        Creates the authorization parameters for the Trustpilot Public API.

        The Public API only requires the API key (stored on the credentials/client_id).
        It does not require OAuth2 authentication.

        See also: https://documentation-apidocumentation.trustpilot.com/#Auth
        """
        if not self.__public_auth_params:
            auth = TrustpilotApikeyAuthenticator(token=config["credentials"]["client_id"])
            self.__public_auth_params = {"authenticator": auth}
        return self.__public_auth_params

    def _oauth2_auth_params(self, config: MutableMapping[str, Any]):
        if not self.__oauth2_auth_params:
            auth = TrustpilotOauth2Authenticator(
                config, token_refresh_endpoint="https://api.trustpilot.com/v1/oauth/oauth-business-users-for-applications/refresh"
            )
            self.__oauth2_auth_params = {"authenticator": auth, "api_key": config["credentials"]["client_id"]}
        return self.__oauth2_auth_params

    def _configured_business_units_stream(self, config: MutableMapping[str, Any]) -> ConfiguredBusinessUnits:
        if not self.__configured_business_units_stream:
            public_auth_params = self._public_auth_params(config)
            self.__configured_business_units_stream = ConfiguredBusinessUnits(
                business_unit_names=config["business_units"], **public_auth_params
            )
        return self.__configured_business_units_stream

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            # NOTE: When `config['credentials']['auth_type'] == 'oauth2.0'` is true, we
            # could here use a stream which requires OAuth 2.0 access.
            #
            # We currently don't do that there. 'private_reviews' seems to be too heavy
            # for that and it could be empty.
            business_units = self._configured_business_units_stream(config)
            for stream_slice in business_units.stream_slices(sync_mode=SyncMode.full_refresh):
                next(business_units.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
                return True, None
        except Exception as error:
            return False, f"Unable to connect to Trustpilot API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        public_auth_params = self._public_auth_params(config)

        configured_business_units_stream = self._configured_business_units_stream(config)

        business_unit_names = config["business_units"]
        common_kwargs = {"business_unit_names": business_unit_names}
        incremental_kwargs = {"start_date": pendulum.parse(config["start_date"])}
        pubic_common_kwargs = {**common_kwargs, **public_auth_params}

        # The Public API streams
        streams = [configured_business_units_stream, BusinessUnits(**pubic_common_kwargs)]

        # API streams requiring OAuth 2.0
        if config["credentials"]["auth_type"] == "oauth2.0":
            auth_params = self._oauth2_auth_params(config)
            consumer_common_kwargs = {**common_kwargs, **auth_params}
            consumer_incremental_kwargs = {**consumer_common_kwargs, **incremental_kwargs}

            streams.extend([PrivateReviews(**consumer_incremental_kwargs)])

        return streams

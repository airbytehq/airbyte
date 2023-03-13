#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .auth import (
    TrustpilotApikeyAuthenticator,
    TrustpilotOauth2Authenticator
)

from .streams import (
    _ConfiguredBusinessUnits,
    BusinessUnits,
    PrivateReviews
)


class SourceTrustpilot(AbstractSource):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.__public_auth_params: Mapping[str, Any] = {}
        self.__auth_params: Mapping[str, Any] = {}
        self.__configured_business_units_stream: Optional[_ConfiguredBusinessUnits] = None

    def _public_auth_params(self, config: MutableMapping[str, Any]):
        """
        Creates the authorization parameters for the Trustpilot Public API.

        The Public API only requires the API key (stored on the credentials/client_id).
        It does not require OAuth2 authentication.

        See also: https://documentation-apidocumentation.trustpilot.com/#Auth
        """
        if not self.__public_auth_params:
            auth = TrustpilotApikeyAuthenticator(
                token=config['credentials']['client_id'])
            self.__public_auth_params = {
                'authenticator': auth
            }
        return self.__public_auth_params

    def _auth_params(self, config: MutableMapping[str, Any]):
        if not self.__auth_params:
            auth = TrustpilotOauth2Authenticator(
                config,
                token_refresh_endpoint="https://api.trustpilot.com/v1/oauth/oauth-business-users-for-applications/refresh"
            )
            self.__auth_params = {
                'authenticator': auth,
                'api_key': config['credentials']['client_id']
            }
        return self.__auth_params

    def _configured_business_units_stream(self, config: MutableMapping[str, Any]) -> _ConfiguredBusinessUnits:
        if not self.__configured_business_units_stream:
            public_auth_params = self._public_auth_params(config)
            self.__configured_business_units_stream = _ConfiguredBusinessUnits(
                business_unit_names=config['business_units'],
                **public_auth_params)
        return self.__configured_business_units_stream

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            business_units = self._configured_business_units_stream(config)
            for stream_slice in business_units.stream_slices(sync_mode=SyncMode.full_refresh):
                next(business_units.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
                return True, None
        except Exception as error:
            import traceback
            return False, f"Unable to connect to Trustpilot API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth_params = self._auth_params(config)

        business_unit_names = config['business_units']
        common_kwargs = {"business_unit_names": business_unit_names, **auth_params}
        incremental_kwargs = {**common_kwargs, **{"start_date": pendulum.parse(config['start_date'])}}

        return [
            BusinessUnits(**common_kwargs),
            PrivateReviews(**incremental_kwargs)
        ]

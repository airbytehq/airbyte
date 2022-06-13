#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
from datetime import datetime, timedelta
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import Annotations, CohortMembers, Cohorts, Engage, Export, Funnels, FunnelsList, Revenue
from .testing import adapt_streams_if_testing


class TokenAuthenticatorBase64(TokenAuthenticator):
    def __init__(self, token: str, auth_method: str = "Basic", **kwargs):
        token = base64.b64encode(token.encode("utf8")).decode("utf8")
        super().__init__(token=token, auth_method=auth_method, **kwargs)


class SourceMixpanel(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            auth = TokenAuthenticatorBase64(token=config["api_secret"])
            funnels = FunnelsList(authenticator=auth, **config)
            response = requests.request(
                "GET",
                url=funnels.url_base + funnels.path(),
                headers={
                    "Accept": "application/json",
                    **auth.get_auth_header(),
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

    @adapt_streams_if_testing
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        tzone = pendulum.timezone(config.get("project_timezone", "US/Pacific"))
        now = datetime.now(tzone).date()

        start_date = config.get("start_date")
        if start_date and isinstance(start_date, str):
            start_date = pendulum.parse(config["start_date"]).date()
        config["start_date"] = start_date or now - timedelta(days=365)

        end_date = config.get("end_date")
        if end_date and isinstance(end_date, str):
            end_date = pendulum.parse(end_date).date()
        config["end_date"] = end_date or now  # set to now by default

        AirbyteLogger().log("INFO", f"Using start_date: {config['start_date']}, end_date: {config['end_date']}")

        auth = TokenAuthenticatorBase64(token=config["api_secret"])
        return [
            Annotations(authenticator=auth, **config),
            Cohorts(authenticator=auth, **config),
            CohortMembers(authenticator=auth, **config),
            Engage(authenticator=auth, **config),
            Export(authenticator=auth, **config),
            Funnels(authenticator=auth, **config),
            Revenue(authenticator=auth, **config),
        ]

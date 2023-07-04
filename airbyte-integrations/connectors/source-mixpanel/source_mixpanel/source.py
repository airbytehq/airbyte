#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import json
import logging
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator, TokenAuthenticator

from .streams import Annotations, CohortMembers, Cohorts, Engage, Export, Funnels, Revenue
from .testing import adapt_streams_if_testing, adapt_validate_if_testing
from .utils import read_full_refresh


class TokenAuthenticatorBase64(TokenAuthenticator):
    def __init__(self, token: str):
        token = base64.b64encode(token.encode("utf8")).decode("utf8")
        super().__init__(token=token, auth_method="Basic")


class SourceMixpanel(AbstractSource):
    def get_authenticator(self, config: Mapping[str, Any]) -> TokenAuthenticator:
        credentials = config.get("credentials")
        if credentials:
            username = credentials.get("username")
            secret = credentials.get("secret")
            if username and secret:
                return BasicHttpAuthenticator(username=username, password=secret)
            return TokenAuthenticatorBase64(token=credentials["api_secret"])
        return TokenAuthenticatorBase64(token=config["api_secret"])

    @adapt_validate_if_testing
    def _validate_and_transform(self, config: Mapping[str, Any]):
        logger = logging.getLogger("airbyte")
        source_spec = self.spec(logger)
        default_project_timezone = source_spec.connectionSpecification["properties"]["project_timezone"]["default"]
        config["project_timezone"] = pendulum.timezone(config.get("project_timezone", default_project_timezone))

        today = pendulum.today(tz=config["project_timezone"]).date()
        start_date = config.get("start_date")
        if start_date:
            config["start_date"] = pendulum.parse(start_date).date()
        else:
            config["start_date"] = today.subtract(days=365)

        end_date = config.get("end_date")
        if end_date:
            config["end_date"] = pendulum.parse(end_date).date()
        else:
            config["end_date"] = today

        for k in ["attribution_window", "select_properties_by_default", "region", "date_window_size"]:
            if k not in config:
                config[k] = source_spec.connectionSpecification["properties"][k]["default"]

        auth = self.get_authenticator(config)
        if isinstance(auth, TokenAuthenticatorBase64) and "project_id" in config:
            config.pop("project_id")
        elif isinstance(auth, BasicHttpAuthenticator) and "project_id" not in config:
            raise ValueError("missing required parameter 'project_id'")

        return config

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            config = self._validate_and_transform(config)
            auth = self.get_authenticator(config)
        except Exception as e:
            return False, e

        # https://github.com/airbytehq/airbyte/pull/27252
        # https://github.com/airbytehq/oncall/issues/2363
        # On one hand there's a number of APIs that is limited by the account plan, so we should probably try to connect to each stream.
        # On the other hand, we have a 30 seconds timeout for this operation and connecting to each stream may take up to one minute.
        # That's why we're validating connectivity by only reading from the stream we definitely know is available independent of a plan.

        try:
            stream = Export(authenticator=auth, reqs_per_hour_limit=0, **config)
            next(read_full_refresh(stream), None)
        except Exception as e:
            try:
                reason = e.response.json()["error"]
                return False, reason
            except json.decoder.JSONDecodeError:
                return False, e
        return True, None

    @adapt_streams_if_testing
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = self._validate_and_transform(config)
        logger = logging.getLogger("airbyte")
        logger.info(f"Using start_date: {config['start_date']}, end_date: {config['end_date']}")

        auth = self.get_authenticator(config)
        streams = [
            Export(authenticator=auth, **config),
        ]

        # we only make calls to one stream of each API type to save time, based on the assumption that
        # if one stream of the API type is available, all others are available as well and vice versa

        streams_by_api_types = [
            [
                Annotations,
            ],
            [Engage, Cohorts, CohortMembers, Funnels, Revenue],
        ]
        for stream_set in streams_by_api_types:
            # set reqs_per_hour_limit = 0 to save time for discovery
            current_stream_set = [stream(authenticator=auth, reqs_per_hour_limit=0, **config) for stream in stream_set]
            test_stream, *_ = current_stream_set
            try:
                next(read_full_refresh(test_stream), None)
            except requests.HTTPError as e:
                if e.response.status_code != 402:
                    raise e
                logger.warning(
                    f"Streams {', '.join([stream.name for stream in current_stream_set])} are disabled, reason: 402 Payment Required"
                )
            else:
                streams.extend(current_stream_set)

        for stream in streams:
            # roll back to default value
            stream.reqs_per_hour_limit = stream.DEFAULT_REQS_PER_HOUR_LIMIT
        return streams

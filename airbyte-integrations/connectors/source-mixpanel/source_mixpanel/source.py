#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import json
import logging
import os
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator, TokenAuthenticator
from airbyte_cdk.utils import AirbyteTracedException

from .streams import Annotations, CohortMembers, Cohorts, Engage, Export, Funnels, Revenue
from .testing import adapt_streams_if_testing, adapt_validate_if_testing
from .utils import read_full_refresh


def raise_config_error(message: str, original_error: Optional[Exception] = None):
    config_error = AirbyteTracedException(message=message, internal_message=message, failure_type=FailureType.config_error)
    if original_error:
        raise config_error from original_error
    raise config_error


class TokenAuthenticatorBase64(TokenAuthenticator):
    def __init__(self, token: str):
        token = base64.b64encode(token.encode("utf8")).decode("utf8")
        super().__init__(token=token, auth_method="Basic")


class SourceMixpanel(AbstractSource):
    STREAMS = [Cohorts, CohortMembers, Funnels, Revenue, Export, Annotations, Engage]

    @staticmethod
    def get_authenticator(config: Mapping[str, Any]) -> TokenAuthenticator:
        credentials = config["credentials"]
        username = credentials.get("username")
        secret = credentials.get("secret")
        if username and secret:
            return BasicHttpAuthenticator(username=username, password=secret)
        return TokenAuthenticatorBase64(token=credentials["api_secret"])

    @staticmethod
    def validate_date(name: str, date_str: str, default: pendulum.date) -> pendulum.date:
        if not date_str:
            return default
        try:
            return pendulum.parse(date_str).date()
        except pendulum.parsing.exceptions.ParserError as e:
            raise_config_error(f"Could not parse {name}: {date_str}. Please enter a valid {name}.", e)

    @adapt_validate_if_testing
    def _validate_and_transform(self, config: MutableMapping[str, Any]):
        project_timezone, start_date, end_date, attribution_window, select_properties_by_default, region, date_window_size, project_id = (
            config.get("project_timezone", "US/Pacific"),
            config.get("start_date"),
            config.get("end_date"),
            config.get("attribution_window", 5),
            config.get("select_properties_by_default", True),
            config.get("region", "US"),
            config.get("date_window_size", 30),
            config.get("credentials", dict()).get("project_id"),
        )
        try:
            project_timezone = pendulum.timezone(project_timezone)
        except pendulum.tz.zoneinfo.exceptions.InvalidTimezone as e:
            raise_config_error(f"Could not parse time zone: {project_timezone}, please enter a valid timezone.", e)

        if region not in ("US", "EU"):
            raise_config_error("Region must be either EU or US.")

        if select_properties_by_default not in (True, False, "", None):
            raise_config_error("Please provide a valid True/False value for the `Select properties by default` parameter.")

        if not isinstance(attribution_window, int) or attribution_window < 0:
            raise_config_error("Please provide a valid integer for the `Attribution window` parameter.")
        if not isinstance(date_window_size, int) or date_window_size < 1:
            raise_config_error("Please provide a valid integer for the `Date slicing window` parameter.")

        auth = self.get_authenticator(config)
        if isinstance(auth, TokenAuthenticatorBase64) and project_id:
            config.get("credentials").pop("project_id")
        if isinstance(auth, BasicHttpAuthenticator) and not isinstance(project_id, int):
            raise_config_error("Required parameter 'project_id' missing or malformed. Please provide a valid project ID.")

        today = pendulum.today(tz=project_timezone).date()
        config["project_timezone"] = project_timezone
        config["start_date"] = self.validate_date("start date", start_date, today.subtract(days=365))
        config["end_date"] = self.validate_date("end date", end_date, today)
        config["attribution_window"] = attribution_window
        config["select_properties_by_default"] = select_properties_by_default
        config["region"] = region
        config["date_window_size"] = date_window_size
        config["project_id"] = project_id

        return config

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        config = self._validate_and_transform(config)
        auth = self.get_authenticator(config)

        # https://github.com/airbytehq/airbyte/pull/27252#discussion_r1228356872
        # temporary solution, testing access for all streams to avoid 402 error
        stream_kwargs = {"authenticator": auth, "reqs_per_hour_limit": 0, **config}
        reason = None
        for stream_class in self.STREAMS:
            try:
                stream = stream_class(**stream_kwargs)
                next(read_full_refresh(stream), None)
                return True, None
            except requests.HTTPError as e:
                try:
                    reason = e.response.json()["error"]
                except json.JSONDecoder:
                    reason = e.response.content
                if e.response.status_code != 402:
                    return False, reason
                logger.info(f"Stream {stream_class.__name__}: {e.response.json()['error']}")
            except Exception as e:
                return False, str(e)
        return False, reason

    @adapt_streams_if_testing
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = self._validate_and_transform(config)
        logger = logging.getLogger("airbyte")
        logger.info(f"Using start_date: {config['start_date']}, end_date: {config['end_date']}")

        auth = self.get_authenticator(config)
        stream_kwargs = {"authenticator": auth, "reqs_per_hour_limit": 0, **config}
        streams = []
        for stream_cls in self.STREAMS:
            stream = stream_cls(**stream_kwargs)
            try:
                stream.get_json_schema()
                next(read_full_refresh(stream), None)
            except requests.HTTPError as e:
                if e.response.status_code != 402:
                    raise e
                logger.warning("Stream '%s' - is disabled, reason: 402 Payment Required", stream.name)
            else:
                reqs_per_hour_limit = int(os.environ.get("REQS_PER_HOUR_LIMIT", stream.DEFAULT_REQS_PER_HOUR_LIMIT))
                # We preserve sleeping between requests in case this is not a running acceptance test.
                # Otherwise, we do not want to wait as each API call is followed by sleeping ~60 seconds.
                stream.reqs_per_hour_limit = reqs_per_hour_limit
                streams.append(stream)
        return streams

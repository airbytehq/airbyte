#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import base64
import copy
import logging
import os
from functools import wraps
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests

from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import BasicHttpAuthenticator, TokenAuthenticator
from airbyte_cdk.utils import AirbyteTracedException
from source_mixpanel.streams import Export


def adapt_validate_if_testing(func):
    """
    Due to API limitations (60 requests per hour) it is impossible to run acceptance tests in normal mode,
    so we're reducing amount of requests by aligning start date if `AVAILABLE_TESTING_RANGE_DAYS` flag is set in env variables.
    """

    @wraps(func)
    def wrapper(self, config):
        config = func(self, config)
        available_testing_range_days = int(os.environ.get("AVAILABLE_TESTING_RANGE_DAYS", 0))
        if available_testing_range_days:
            logger = logging.getLogger("airbyte")
            logger.info("SOURCE IN TESTING MODE, DO NOT USE IN PRODUCTION!")
            if (config["end_date"] - config["start_date"]).days > available_testing_range_days:
                config["start_date"] = config["end_date"].subtract(days=available_testing_range_days)
        return config

    return wrapper


def raise_config_error(message: str, original_error: Optional[Exception] = None):
    config_error = AirbyteTracedException(message=message, internal_message=message, failure_type=FailureType.config_error)
    if original_error:
        raise config_error from original_error
    raise config_error


class TokenAuthenticatorBase64(TokenAuthenticator):
    def __init__(self, token: str):
        token = base64.b64encode(token.encode("utf8")).decode("utf8")
        super().__init__(token=token, auth_method="Basic")


SUPPORTED_REGIONS = ("US", "EU")
REGION_PROBE_TIMEOUT_SECONDS = 30


class SourceMixpanel(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    @staticmethod
    def _region_api_base(region: str) -> str:
        """Return the Mixpanel API base URL for a data-residency `region`, mirroring `manifest.yaml`."""
        prefix = "" if region == "US" else f"{region}."
        return f"https://{prefix}mixpanel.com/api/"

    def _region_authenticates(self, logger: logging.Logger, config: Mapping[str, Any], region: str) -> Optional[bool]:
        """Return whether the configured credentials authenticate against a given `region`'s Mixpanel host.

        Makes a single, bounded, authenticated request to the cheap `query/cohorts/list` endpoint and returns:

        - `True` when the credentials are valid for that region (`2xx`).
        - `False` when the region explicitly rejects the credentials (`401`/`403`).
        - `None` when the outcome is inconclusive (network error, `5xx`, or any other status), so a transient
          failure never manufactures a residency mismatch.
        """
        auth = self.get_authenticator(config)
        headers = {"Accept": "application/json", **auth.get_auth_header()}
        project_id = config.get("credentials", {}).get("project_id")
        params = {"project_id": project_id} if project_id else {}
        url = f"{self._region_api_base(region)}query/cohorts/list"
        try:
            response = requests.get(url, headers=headers, params=params, timeout=REGION_PROBE_TIMEOUT_SECONDS)
        except requests.RequestException as e:
            logger.info(f"Data residency probe against the {region} region was inconclusive: {e}")
            return None
        if response.ok:
            return True
        if response.status_code in (401, 403):
            return False
        logger.info(f"Data residency probe against the {region} region was inconclusive: HTTP {response.status_code}")
        return None

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """Validate the connection, failing fast with an actionable message on a data-residency mismatch.

        The declarative check can return a false green when `region` is wrong, after which schema discovery
        hangs against the wrong regional host. When the normal check fails, this probes the other supported
        regions; if the credentials authenticate against a different region, it surfaces which `region` to set
        instead of letting the user hit an unexplained discovery timeout.
        """
        connected, error = super().check_connection(logger, config)
        if connected:
            return connected, error

        configured_region = config.get("region", "US")
        if configured_region not in SUPPORTED_REGIONS or self._region_authenticates(logger, config, configured_region) is not False:
            return connected, error

        matching_regions = [
            region
            for region in SUPPORTED_REGIONS
            if region != configured_region and self._region_authenticates(logger, config, region) is True
        ]
        if matching_regions:
            region_list = " or ".join(matching_regions)
            message = (
                f"Mixpanel credentials authenticate against the {region_list} data residency region, "
                f"not the configured {configured_region} region. Set Data Residency to {region_list} and retry."
            )
            return False, message

        return connected, error

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
        (
            project_timezone,
            start_date,
            end_date,
            attribution_window,
            select_properties_by_default,
            region,
            date_window_size,
            project_id,
            page_size,
            export_lookback_window,
        ) = (
            config.get("project_timezone", "US/Pacific"),
            config.get("start_date"),
            config.get("end_date"),
            config.get("attribution_window", 5),
            config.get("select_properties_by_default", True),
            config.get("region", "US"),
            config.get("date_window_size", 30),
            config.get("credentials", dict()).get("project_id"),
            config.get("page_size", 1000),
            config.get("export_lookback_window", 0),
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
        if not isinstance(export_lookback_window, int) or export_lookback_window < 0:
            raise_config_error("Please provide a valid integer for the `Export Lookback Window` parameter.")

        auth = self.get_authenticator(config)
        if isinstance(auth, TokenAuthenticatorBase64) and project_id:
            config.get("credentials").pop("project_id")
        if isinstance(auth, BasicHttpAuthenticator) and not isinstance(project_id, int):
            raise_config_error("Required parameter 'project_id' missing or malformed. Please provide a valid project ID.")

        today = pendulum.today(tz=project_timezone).date()
        config["project_timezone"] = project_timezone
        config["start_date"] = self.validate_date("start date", start_date, today.subtract(days=365))
        config["end_date"] = self.validate_date("end date", end_date, today.subtract(days=1))
        config["attribution_window"] = attribution_window
        config["select_properties_by_default"] = select_properties_by_default
        config["region"] = region
        config["date_window_size"] = date_window_size
        config["project_id"] = project_id
        config["page_size"] = page_size
        config["export_lookback_window"] = export_lookback_window

        return config

    @staticmethod
    def get_authenticator(config: Mapping[str, Any]) -> TokenAuthenticator:
        credentials = config["credentials"]
        username = credentials.get("username")
        secret = credentials.get("secret")
        if username and secret:
            return BasicHttpAuthenticator(username=username, password=secret)
        return TokenAuthenticatorBase64(token=credentials["api_secret"])

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        credentials = config.get("credentials")
        if not credentials.get("option_title"):
            if credentials.get("api_secret"):
                credentials["option_title"] = "Project Secret"
            else:
                credentials["option_title"] = "Service Account"

        streams = super().streams(config=config)

        config_transformed = copy.deepcopy(config)
        config_transformed = self._validate_and_transform(config_transformed)
        auth = self.get_authenticator(config)

        streams.append(Export(authenticator=auth, **config_transformed))

        return streams

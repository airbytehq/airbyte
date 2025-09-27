#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import logging
from base64 import standard_b64encode
from typing import Any, List, Mapping, Optional

import pendulum

from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from airbyte_cdk.utils import AirbyteTracedException

from .reports.reports import CustomReport
from .streams import AdAccounts, AdAccountValidationStream, PinterestStream


logger = logging.getLogger("airbyte")


class SourcePinterest(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    @staticmethod
    def _validate_and_transform(config: Mapping[str, Any], amount_of_days_allowed_for_lookup: int = 89) -> Mapping[str, Any]:
        transformed_config = copy.deepcopy(config)
        today = pendulum.today()
        latest_date_allowed_by_api = today.subtract(days=amount_of_days_allowed_for_lookup)

        start_date = transformed_config.get("start_date")

        # transform to datetime
        if start_date and isinstance(start_date, str):
            try:
                transformed_config["start_date"] = pendulum.from_format(start_date, "YYYY-MM-DD")
            except ValueError:
                message = f"Entered `Start Date` {start_date} does not match format YYYY-MM-DD"
                raise AirbyteTracedException(
                    message=message,
                    internal_message=message,
                    failure_type=FailureType.config_error,
                )

        if not start_date or transformed_config["start_date"] < latest_date_allowed_by_api:
            logger.info(
                f"Current start_date: {start_date} does not meet API report requirements. "
                f"Resetting start_date to: {latest_date_allowed_by_api}"
            )
            transformed_config["start_date"] = latest_date_allowed_by_api

            # Check if account_id exists
        if "account_id" in transformed_config:
            validation_stream = AdAccountValidationStream(config)
            response = list(validation_stream.read_records(sync_mode=SyncMode.full_refresh))

            if not response:
                raise AirbyteTracedException(
                    message=f"Invalid ad_account_id: {transformed_config['account_id']}. No data returned from Pinterest API.",
                    internal_message="The provided ad_account_id does not exist.",
                    failure_type=FailureType.config_error,
                )

        return transformed_config

    @staticmethod
    def get_authenticator(config) -> Oauth2Authenticator:
        config = config.get("credentials") or config
        credentials_base64_encoded = standard_b64encode(
            (config.get("client_id") + ":" + config.get("client_secret")).encode("ascii")
        ).decode("ascii")
        auth = f"Basic {credentials_base64_encoded}"

        return Oauth2Authenticator(
            token_refresh_endpoint=f"{PinterestStream.url_base}oauth/token",
            client_secret=config.get("client_secret"),
            client_id=config.get("client_id"),
            refresh_request_headers={"Authorization": auth},
            refresh_token=config.get("refresh_token"),
        )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        declarative_streams = super().streams(config)

        transformed_config = copy.deepcopy(config)
        transformed_config["authenticator"] = self.get_authenticator(transformed_config)
        transformed_config = self._validate_and_transform(transformed_config, amount_of_days_allowed_for_lookup=913)

        # Report streams involve async data fetch, which is currently not supported in low-code
        ad_accounts = AdAccounts(transformed_config)
        custom_report_streams = self.get_custom_report_streams(config=transformed_config, ad_accounts_stream=ad_accounts)

        return declarative_streams + custom_report_streams

    def get_custom_report_streams(self, config: Mapping[str, Any], ad_accounts_stream: AdAccounts) -> List[Stream]:
        """return custom report streams"""
        custom_streams = []
        for report_config in config.get("custom_reports", []):
            report_config["authenticator"] = config["authenticator"]

            # https://developers.pinterest.com/docs/api/v5/#operation/analytics/get_report
            if report_config.get("granularity") == "HOUR":
                # Otherwise: Response Code: 400 {"code":1,"message":"HOURLY request must be less than 3 days"}
                amount_of_days_allowed_for_lookup = 2
            elif report_config.get("level") == "PRODUCT_ITEM":
                amount_of_days_allowed_for_lookup = 91
            else:
                amount_of_days_allowed_for_lookup = 913

            start_date = report_config.get("start_date")
            if not start_date:
                report_config["start_date"] = config.get("start_date")

            report_config = self._validate_and_transform(report_config, amount_of_days_allowed_for_lookup)

            stream = CustomReport(parent=ad_accounts_stream, config=report_config)
            custom_streams.append(stream)
        return custom_streams

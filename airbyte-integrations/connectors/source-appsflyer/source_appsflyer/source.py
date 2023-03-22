#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from datetime import timedelta
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_appsflyer.streams import InAppEvents, Installs, RetargetingInAppEvents, DailyReport, GeoReport, \
    RetargetingPartnersReport, RetargetingGeoReport, RetargetingDailyReport, PartnersReport, RetargetingConversions, \
    UninstallEvents, parse_date
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class SourceAppsflyer(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            timezone = config.get("timezone", "UTC")
            if timezone not in pendulum.timezones:
                return False, "The supplied timezone is invalid."
            app_id = config["app_id"]
            api_token = config["api_token"]
            dates = pendulum.now("UTC").to_date_string()
            test_url = (
                f"https://hq.appsflyer.com/export/{app_id}/partners_report/v5?api_token={api_token}&from={dates}&to={dates}&timezone=UTC"
            )
            response = requests.request("GET", url=test_url)

            if response.status_code != 200:
                error_message = "The supplied APP ID is invalid" if response.status_code == 404 else response.text.rstrip("\n")
                if error_message:
                    return False, error_message
                response.raise_for_status()
        except Exception as e:
            return False, e

        return True, None

    def is_start_date_before_earliest_date(self, start_date, earliest_date):
        if start_date <= earliest_date:
            AirbyteLogger().log("INFO", f"Start date over 90 days, using start_date: {earliest_date}")
            return earliest_date

        return start_date

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["timezone"] = config.get("timezone", "UTC")
        timezone = pendulum.timezone(config.get("timezone", "UTC"))
        earliest_date = pendulum.today(timezone) - timedelta(days=90)
        start_date = parse_date(config.get("start_date") or pendulum.today(timezone), timezone)
        config["start_date"] = self.is_start_date_before_earliest_date(start_date, earliest_date)
        config["end_date"] = pendulum.now(timezone)
        auth = TokenAuthenticator(token=config.get("api_token"), auth_method="Bearer")
        return [
            InAppEvents(authenticator=auth, **config),
            Installs(authenticator=auth, **config),
            UninstallEvents(authenticator=auth, **config),
            RetargetingInAppEvents(authenticator=auth, **config),
            RetargetingConversions(authenticator=auth, **config),
            PartnersReport(authenticator=auth, **config),
            DailyReport(authenticator=auth, **config),
            GeoReport(authenticator=auth, **config),
            RetargetingPartnersReport(authenticator=auth, **config),
            RetargetingDailyReport(authenticator=auth, **config),
            RetargetingGeoReport(authenticator=auth, **config),
        ]

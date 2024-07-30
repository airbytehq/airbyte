#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from datetime import datetime, timedelta

from .streams import (
    PendoPythonStream,
    Feature,
    Guide,
    Page,
    Report,
    ReportResult,
    VisitorMetadata,
    AccountMetadata,
    Visitor,
    Account,
    PageEvents,
    FeatureEvents,
    GuideEvents
)


class PendoAuthenticator(HttpAuthenticator):
    def __init__(self, token: str):
        self._token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Pendo-Integration-Key": self._token}


class SourcePendoPython(AbstractSource):
    @staticmethod
    def _get_authenticator(config: Mapping[str, Any]) -> HttpAuthenticator:
        token = config.get("api_key")
        return PendoAuthenticator(token)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        url = f"{PendoPythonStream.url_base}page"
        auth = SourcePendoPython._get_authenticator(config)
        try:
            session = requests.get(url, headers=auth.get_auth_header())
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def get_reports(self, config):
        url = f"{PendoPythonStream.url_base}report"
        auth = SourcePendoPython._get_authenticator(config)
        try:
            session = requests.get(url, headers=auth.get_auth_header())
            body = session.json()
            return [obj["id"] for obj in body]
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._get_authenticator(config)

        default_start_date = datetime.now() - timedelta(days=2*365)
        start_date = config.get("start_date", default_start_date.strftime('%Y-%m-%dT%H:%M:%S'))
        day_page_size = config.get("day_page_size", 21)

        result = [
            Feature(authenticator=auth),
            Guide(authenticator=auth),
            Page(authenticator=auth),
            Report(authenticator=auth),
            VisitorMetadata(authenticator=auth),
            AccountMetadata(authenticator=auth),
            Visitor(authenticator=auth),
            Account(authenticator=auth),
            PageEvents(start_date=start_date, day_page_size=day_page_size, authenticator=auth),
            FeatureEvents(start_date=start_date, day_page_size=day_page_size, authenticator=auth),
            GuideEvents(start_date=start_date, day_page_size=day_page_size, authenticator=auth)
        ]

        report_allowlist = config.get("report_allowlist")
        if reports and len(report_allowlist) > 0:
            for report_id in report_allowlist:
                result.append(ReportResult(report=report_id, authenticator=auth))
        else:
            all_reports = self.get_reports(config)
            for report in all_reports:
                result.append(ReportResult(report=report, authenticator=auth))

        return result

#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple
import re
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator
from datetime import datetime, timedelta

from .streams import (
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
    GuideEvents,
)


class PendoAuthenticator(AbstractHeaderAuthenticator):
    def __init__(self, token: str):
        self._token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Pendo-Integration-Key": self._token}


class SourcePendoPython(AbstractSource):
    def _url_base(self, config: Mapping[str, Any]) -> str:
        url_base = "https://app.pendo.io/api/v1/" if not re.search(r"\.eu$", config.get("api_key")) else "https://app.eu.pendo.io/api/v1/"
        print(f"url_base as derived from api_key: {url_base}")
        return url_base

    @staticmethod
    def _get_authenticator(config: Mapping[str, Any]) -> AbstractHeaderAuthenticator:
        token = config.get("api_key")
        return PendoAuthenticator(token)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        url = f"{self._url_base(config)}page"
        auth = SourcePendoPython._get_authenticator(config)
        try:
            session = requests.get(url, headers={auth.auth_header: auth.token})
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def get_reports(self, config):
        url = f"{self._url_base(config)}report"
        auth = SourcePendoPython._get_authenticator(config)
        try:
            session = requests.get(url, headers={auth.auth_header: auth.token})
            body = session.json()
            return [obj["id"] for obj in body]
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._get_authenticator(config)

        default_start_date = datetime.now() - timedelta(days=2 * 365)
        start_date = config.get("start_date", default_start_date.strftime("%Y-%m-%dT%H:%M:%S"))
        day_page_size = config.get("day_page_size", 21)

        url_base = self._url_base(config)

        result = [
            Feature(authenticator=auth, url_base=url_base),
            Guide(authenticator=auth, url_base=url_base),
            Page(authenticator=auth, url_base=url_base),
            Report(authenticator=auth, url_base=url_base),
            VisitorMetadata(authenticator=auth, url_base=url_base),
            AccountMetadata(authenticator=auth, url_base=url_base),
            Visitor(authenticator=auth, url_base=url_base),
            Account(authenticator=auth, url_base=url_base),
            PageEvents(start_date=start_date, day_page_size=day_page_size, authenticator=auth, url_base=url_base),
            FeatureEvents(start_date=start_date, day_page_size=day_page_size, authenticator=auth, url_base=url_base),
            GuideEvents(start_date=start_date, day_page_size=day_page_size, authenticator=auth, url_base=url_base),
        ]

        report_allowlist = config.get("report_allowlist")
        if report_allowlist and len(report_allowlist) > 0:
            for report_id in report_allowlist:
                result.append(ReportResult(report=report_id, authenticator=auth, url_base=url_base))
        else:
            all_reports = self.get_reports(config)
            for report in all_reports:
                result.append(ReportResult(report=report, authenticator=auth, url_base=url_base))

        return result

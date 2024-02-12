from __future__ import annotations

import csv
import io
import time
import zipfile
from datetime import date
from pathlib import Path
from typing import List, Type, Mapping, Any, Iterable, Dict, TextIO, Optional, Union
from urllib.parse import urljoin

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream

from source_ozon.auth import OzonToken
from source_ozon.schemas.banner_report_data import BannerReport
from source_ozon.schemas.brend_shelf_report_data import BrandShelfReport
from source_ozon.schemas.campaign import OzonCampaign, CampaignReport
from source_ozon.schemas.report import ReportStatusResponse
from source_ozon.schemas.search_promo_report_data import SearchPromoReport
from source_ozon.schemas.sku_report_data import SkuReport
from source_ozon.types import IsSuccess, Message
from source_ozon.utils import chunks, pairwise, get_dates_between

_CAMPAIGN_TYPES_WITHOUT_DATE: set[str] = {"BANNER", "BRAND_SHELF", "SKU"}


def check_ozon_api_connection(credentials: OzonToken) -> tuple[IsSuccess, Optional[Message]]:
    try:
        response = requests.get(
            url="https://performance.ozon.ru/api/client/campaign",
            headers={"Authorization": f"Bearer {credentials.access_token.get_secret_value()}"},
        )
        response.raise_for_status()
        return True, None
    except Exception as e:
        print(f"Ozon API connection check failed: {str(e)}")
        return False, str(e)


class CampaignsReportStream(Stream):
    HOST: str = "https://performance.ozon.ru"
    PATH: str = "/api/client/statistics"
    CAMPAIGNS_PATH: str = "/api/client/campaign"
    SCHEMA: Type[CampaignReport] = CampaignReport

    @property
    def full_url(self) -> str:
        return urljoin(self.HOST, self.PATH)

    @property
    def campaigns_url(self) -> str:
        return urljoin(self.HOST, self.CAMPAIGNS_PATH)

    def __init__(self, credentials: OzonToken, date_from: date, date_to: date):
        self.credentials = credentials
        self.date_from = date_from
        self.date_to = date_to

        self._campaigns_by_ids: Dict[str, OzonCampaign] = {}
        self._campaigns_by_report_ids: Dict[str, OzonCampaign] = {}
        self._request_bodies: List[Dict[str, Union[List[str], str]]] = []

    @property
    def primary_key(self) -> None:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.SCHEMA.schema()

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self._set_campaigns()
        self._set_request_bodies()
        for request_body in self._request_bodies:
            yield from self._run_report(request_body)

    def _get_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.credentials.access_token.get_secret_value()}"}

    def _set_campaigns(self) -> None:
        try:
            response = requests.get(self.campaigns_url, headers=self._get_headers())
            response.raise_for_status()
            response_data = response.json()
        except Exception as e:
            print(f"Fail to get Ozon campaigns: {str(e)}")
            raise

        if not (campaigns := response_data.get("list", [])):
            print(f"There is no campaigns in Ozon")
            return

        for campaign in campaigns:
            try:
                campaign_ = OzonCampaign(**campaign)
                self._campaigns_by_ids[campaign_.id] = campaign_
            except Exception as e:
                print(f"Fail to parse Ozon campaigns: {str(e)}")
                raise

        print(f"Got {len(campaigns)} Ozon campaigns")

    def _set_request_bodies(self) -> None:
        if not self._campaigns_by_ids:
            return

        campaigns: List[OzonCampaign] = list(self._campaigns_by_ids.values())
        campaigns_with_date: List[OzonCampaign] = []
        campaigns_without_date: List[OzonCampaign] = []
        for campaign in campaigns:
            if campaign.advObjectType in _CAMPAIGN_TYPES_WITHOUT_DATE:
                campaigns_without_date.append(campaign)
            else:
                campaigns_with_date.append(campaign)

        for chunk in chunks(campaigns_with_date, 10):
            self._request_bodies.append(
                {
                    "campaigns": [campaign.id for campaign in chunk],
                    "dateFrom": self.date_from.strftime("%Y-%m-%d"),
                    "dateTo": self.date_to.strftime("%Y-%m-%d"),
                }
            )

        for date_str in get_dates_between(date_from=self.date_from, date_to=self.date_to):
            for chunk in chunks(campaigns_without_date, 10):
                self._request_bodies.append(
                    {
                        "campaigns": [campaign.id for campaign in chunk],
                        "dateFrom": date_str,
                        "dateTo": date_str,
                    }
                )

        print(f"{len(self._request_bodies)} Ozon reports will be created")

    def _run_report(self, request_body: Dict[str, Union[List[str], str]]) -> Iterable[Mapping[str, Any]]:
        request_campaign_ids = request_body["campaigns"]
        request_date_from = request_body["dateFrom"]
        request_date_to = request_body["dateTo"]
        campaigns_len = len(request_campaign_ids)

        if request_date_from == request_date_to:
            for campaign_id in request_campaign_ids:
                campaign = self._campaigns_by_ids[campaign_id]
                campaign.date = request_date_from

        report_id = self._create_report(request_body)

        if campaigns_len == 1:
            campaign = self._campaigns_by_ids[request_campaign_ids[0]]
            self._campaigns_by_report_ids[report_id] = campaign

        report_download_link = self._wait_for_report_processing(report_id)
        report_file = self._download_report(
            download_link=report_download_link,
            filepath=self._get_report_file_path(report_id, campaigns_len=campaigns_len),
        )
        try:
            yield from self._parse_report(report_filepath=report_file)
        finally:
            report_file.unlink(missing_ok=True)

    def _create_report(self, request_body: Dict[str, Union[List[str], str]]) -> str:
        try:
            response = requests.post(self.full_url, headers=self._get_headers(), json=request_body)
            response.raise_for_status()
            response_data = response.json()
        except Exception as e:
            print(f"Fail to create Ozon campaign report: {str(e)}")
            raise
        else:
            if error := response_data.get("error"):
                print(f"Fail to create Ozon campaign report: {error}")
                raise RuntimeError(f"Fail to create Ozon campaign report: {error}")

            if (report_id := response_data.get("UUID")) is None:
                print(f"Report ID not found in create report response: {response_data}")
                raise ValueError(f"Report ID not found in create report response: {response_data}")

            print(f"Ozon report created: {report_id}")
            return report_id

    def _wait_for_report_processing(self, report_id: str) -> str:
        url = f"{self.full_url}/{report_id}"
        print(f"Report {report_id} status check URL: {url}")

        errors_counter = 0
        while True:
            try:
                response = requests.get(url, headers=self._get_headers())
                response.raise_for_status()
            except Exception as e:
                print(f"Fail to get report status: {str(e)}")
                errors_counter += 1
                if errors_counter > 5:
                    raise RuntimeError(f"Failed to check report {report_id} status {errors_counter} times") from e
                time.sleep(60)
                continue
            else:
                report_status = ReportStatusResponse(**response.json())
                print(f"Report {report_id} state: {report_status.state}")

                if report_status.state == "OK":
                    download_link = self.HOST + report_status.link
                    print(f"Report {report_id} download URL: {download_link}")
                    return download_link

                if report_status.state == "ERROR":
                    print(f"Report {report_id} failed: {report_status.error}")
                    raise RuntimeError(f"Report {report_id} failed: {report_status.error}")

                time.sleep(10)

    @staticmethod
    def _get_report_file_path(report_id: str, campaigns_len: int) -> Path:
        filename = f"{report_id}.csv" if campaigns_len == 1 else f"{report_id}.zip"
        return Path(__file__).parent.resolve() / filename

    def _download_report(self, download_link: str, filepath: Path) -> Path:
        try:
            response = requests.get(download_link, stream=True, headers=self._get_headers())
            response.raise_for_status()
            with open(filepath, "wb") as file:
                for chunk in response.iter_content(chunk_size=128):
                    file.write(chunk)
            print(f"Download complete: {filepath}")
            return filepath
        except Exception as e:
            print(f"Fail to download report: {str(e)}")
            raise RuntimeError(f"Fail to download report: {str(e)}") from e

    def _parse_report(self, report_filepath: Path) -> Iterable[Mapping[str, Any]]:
        file_extension = report_filepath.suffix
        if file_extension == ".zip":
            with zipfile.ZipFile(report_filepath, "r") as z:
                for filename in z.namelist():
                    if filename.endswith(".csv"):
                        campaign = self._get_campaign_by_campaign_report_name(filename)
                        with z.open(filename) as csvfile:
                            textfile = io.TextIOWrapper(csvfile, encoding="utf-8")
                            yield from self._read_csv(textfile, campaign)
                    else:
                        print(f"Unknown report file extension in zip archive '{report_filepath.name}': '{filename}'")
                        raise ValueError(f"Unknown report file extension in zip archive '{report_filepath.name}': '{filename}'")

        elif file_extension == ".csv":
            campaign = self._get_campaign_by_campaign_report_name(report_filepath.name)
            with open(report_filepath, newline="", encoding="utf-8") as csvfile:
                yield from self._read_csv(csvfile, campaign)

        else:
            print(f"Unknown report file extension: {report_filepath.name}")
            raise ValueError(f"Unknown report file extension: {report_filepath.name}")

    def _get_campaign_by_campaign_report_name(self, filename: str) -> OzonCampaign:
        campaign_id = filename.split("_")[0]
        try:
            return self._campaigns_by_ids[campaign_id]
        except KeyError:
            report_id = filename.split(".")[0]
            try:
                return self._campaigns_by_report_ids[report_id]
            except KeyError as e:
                print(f"Unknown Ozon campaign: '{campaign_id}'")
                raise ValueError(f"Unknown Ozon campaign: '{campaign_id}'") from e

    def _read_csv(self, csv_file: TextIO, campaign: OzonCampaign) -> Iterable[Mapping[str, Any]]:
        csvreader = csv.reader(csv_file, delimiter=";")
        report_schema = self._get_campaign_schema(campaign)
        next(csvreader, None)  # Skip report header
        columns_headers = next(csvreader, None)
        for current_row, next_row in pairwise(csvreader):
            if current_row[0] == "Корректировка":  # Не учитываем корректировку
                continue
            try:
                row = self.SCHEMA(
                    campaign_id=campaign.id,
                    campaign_name=campaign.title,
                    campaign_type=campaign.advObjectType,
                )
                row.report_data = report_schema.parse_obj(dict(zip(columns_headers, current_row)))
                if campaign.date:
                    row.report_data.date = campaign.date
                assert row.report_data.date
                yield row.dict()
            except Exception as e:
                print(f"Failed to parse Ozon report for campaign '{campaign.id}': {str(e)}")
                raise RuntimeError(f"Failed to parse Ozon report for campaign '{campaign.id}': {str(e)}") from e

    @staticmethod
    def _get_campaign_schema(campaign: OzonCampaign) -> Type[SearchPromoReport | BannerReport | BrandShelfReport | SkuReport]:
        if campaign.advObjectType == "SEARCH_PROMO":
            return SearchPromoReport
        elif campaign.advObjectType == "BANNER":
            return BannerReport
        elif campaign.advObjectType == "BRAND_SHELF":
            return BrandShelfReport
        elif campaign.advObjectType == "SKU":
            return SkuReport
        else:
            print(f"Unknown Ozon campaign '{campaign.id}' type: '{campaign.advObjectType}'")
            raise ValueError(f"Unknown Ozon campaign '{campaign.id}' type: '{campaign.advObjectType}'")

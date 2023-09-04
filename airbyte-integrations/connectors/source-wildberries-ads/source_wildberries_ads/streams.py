from __future__ import annotations

import time
from abc import ABC
from datetime import date
from typing import Type, Mapping, Any, Dict, List, Iterable, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from requests.exceptions import ChunkedEncodingError

from source_wildberries_ads.schemas.autostat import AdsAutoStat
from source_wildberries_ads.schemas.fullstat import AdsFullStat
from source_wildberries_ads.schemas.seacatstat import AdsSeaCatStat
from source_wildberries_ads.schemas.words import AdsWordsStat
from source_wildberries_ads.types import WildberriesCredentials, IsSuccess, Message, SchemaT


def check_ads_stream_connection(credentials: WildberriesCredentials, campaign_id: int) -> tuple[IsSuccess, Optional[Message]]:
    url = f"https://advert-api.wb.ru/adv/v1/stat/words?id={campaign_id}"
    headers = {"Authorization": credentials["api_key"]}
    try:
        response = requests.get(url, headers=headers)
        if 200 <= response.status_code < 300:
            return True, None
        elif response.status_code == 400:
            return False, f"Campaign not found by campaign ID. Response status code: {response.status_code}"
        elif response.status_code == 401:
            return False, f"Invalid ads API key. Response status code: {response.status_code}. Body: {response.text}"
        else:
            return False, f"Response status code: {response.status_code}. Body: {response.text}"
    except Exception as e:
        return False, str(e)


class AdsStream(Stream, ABC):
    SCHEMA: Type[SchemaT] = NotImplemented
    URL: str = NotImplemented

    def __init__(self, credentials: WildberriesCredentials, campaign_id: int):
        self.credentials = credentials
        self.campaign_id = campaign_id

    @property
    def primary_key(self) -> None:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.SCHEMA.schema()

    @property
    def url(self) -> str:
        return self.URL + f"?id={self.campaign_id}"

    @property
    def headers(self) -> Dict:
        return {"Authorization": self.credentials["api_key"]}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        attempts_count = 0
        while attempts_count < 3:
            try:
                response = requests.get(self.url, headers=self.headers)
            except ChunkedEncodingError:
                time.sleep(60)
                continue
            if response.status_code == 200:
                if record := response.json():
                    yield self.SCHEMA(**record).dict()
                return
            elif response.status_code == 204:
                return
            elif response.status_code > 500:
                time.sleep(60)
                continue
            elif response.status_code in (408, 429):
                attempts_count += 1
                if attempts_count < 3:
                    time.sleep(60)  # Wait for Wildberries rate limits
                else:
                    raise Exception(f"Failed to load data from Wildberries API after 3 attempts due to rate limits")
            else:
                raise Exception(f"Status code: {response.status_code}. Body: {response.text}")


class WordsStatStream(AdsStream):
    SCHEMA: Type[AdsWordsStat] = AdsWordsStat
    URL: str = "https://advert-api.wb.ru/adv/v1/stat/words"


class FullStatStream(AdsStream):
    SCHEMA: Type[AdsFullStat] = AdsFullStat
    URL: str = "https://advert-api.wb.ru/adv/v1/fullstat"

    def __init__(self, credentials: WildberriesCredentials, campaign_id: int, date_from: date | None, date_to: date | None):
        super().__init__(credentials, campaign_id)
        self.date_from = date_from
        self.date_to = date_to

    @property
    def url(self) -> str:
        url = self.URL + f"?id={self.campaign_id}"
        if self.date_from:
            url += f"&begin={self.date_from.strftime('%Y-%m-%d')}"
        if self.date_to:
            url += f"&end={self.date_to.strftime('%Y-%m-%d')}"
        return url


class AutoStatStream(AdsStream):
    SCHEMA: Type[AdsAutoStat] = AdsAutoStat
    URL: str = "https://advert-api.wb.ru/adv/v1/auto/stat"


class SeaCatStatStream(AdsStream):
    SCHEMA: Type[AdsSeaCatStat] = AdsSeaCatStat
    URL: str = "https://advert-api.wb.ru/adv/v1/seacat/stat"

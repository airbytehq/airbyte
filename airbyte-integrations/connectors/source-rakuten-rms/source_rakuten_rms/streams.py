#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
import time
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from dateutil.parser import parse
import requests
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import (
    EpochValueConcurrentStreamStateConverter,
    IsoMillisConcurrentStreamStateConverter,
)
from abc import ABC, abstractmethod
from datetime import datetime
from airbyte_cdk.models import (
    FailureType,
    SyncMode,
)
from airbyte_cdk.sources.streams import Stream, CheckpointMixin
from airbyte_cdk.sources.streams.availability_strategy import (
    AvailabilityStrategy,
)
from airbyte_cdk.sources.streams.http.error_handlers.backoff_strategy import BackoffStrategy
from .error_mappings.rms_stream_error_mapping import PARENT_INCREMENTAL_RMS_STREAM_ERROR_MAPPING
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.http_status_error_handler import HttpStatusErrorHandler
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType
from datetime import datetime, timedelta, timezone
from .utils import generate_access_token
import base64

# 
_OUTGOING_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

## Inventory API constants 
## 店舗内の商品情報が1000SKUを超える場合は、エラーになる（エラーコード：IE0116?????）
_INVENTORIES_REQUEST_INTERVAL_SECONDS = 0.4 # LIMIT制限を考慮し、0.4秒に設定
_INVENTORIES_RATE_LIMIT = 0.2 # 5req/1secのため

# Navigation API constants
_NAVIGATION_REQUEST_INTERVAL_SECONDS = 0.4
_NAVIGATION_RATE_LIMIT = 0.2

# Items API constants
_ITEMS_REQUEST_INTERVAL_SECONDS = 0.8 # LIMIT制限を考慮し、0.8秒に設定 0.5とかだと429エラーが結構発生しているかも
_ITEMS_RATE_LIMIT = 0.2

# Purchase Item API constants
_PURCHASE_ITEM_REQUEST_INTERVAL_SECONDS = 1 # LIMIT制限を考慮し、1秒に設定

# Categories API constants
_CATEGORIES_REQUEST_INTERVAL_SECONDS = 0.4

# Purchase Order API constants
_PAGE_SIZE = 1000 # per page
_SORT_COLUMN = 1 # Only 1 is available 
_SORT_DIREDCTION = 1 # 1: Ascending, 2: Descending
_START_DATE_DELTA_DAYS= 730 # 2 year ago
_DATE_RANGE = 30 # 63 days
now = datetime.now(timezone(timedelta(hours=9)))  # 日本のタイムゾーン (+0900) # descriptionには+09:00と書いてあるのに設定値は+0900であることに注意

class RakutenErrorHandler(ErrorHandler):
    def __init__(self, logger: logging.Logger, stream_name: str) -> str:
        self._stream_name = stream_name
        self._logger = logger

    @property
    def max_retries(self) -> Optional[int]:
        return 3
    
    @property
    def max_time(self) -> Optional[int]:
        return 60

class RmsSupportBackoffStrategy(BackoffStrategy):
    def backoff_time(
        self,
        response_or_exception: Optional[Union[requests.Response, requests.RequestException]],
        attempt_count: int,
    ) -> Optional[float]:
        if response_or_exception is None:
            return None
        if isinstance(response_or_exception, requests.Response):
            if response_or_exception.status_code == 429:
                return 1.0
        return None

class RakutenRmsBaseStream(HttpStream, ABC):
    """
    Base Class for Rakuten RMS API
    """
    def __init__(self, 
                 config: Mapping[str, Any],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._token = generate_access_token(config["service_secret"], config["licence_key"])

    primary_key: Optional[Union[str, List[str], List[List[str]]]] = None

    # この関数で使っているPARENT_INCREMENTAL_RMS_STREAM_ERROR_MAPPING内のDEFAULT_ERROR_MAPPINGがインポートできない
    def get_error_handler(self) -> ErrorHandler:

        error_mapping = PARENT_INCREMENTAL_RMS_STREAM_ERROR_MAPPING

        return HttpStatusErrorHandler(logger=self.logger, error_mapping=error_mapping, max_retries=self.max_retries)

    def request_headers(
        self, 
        stream_state: Mapping[str, Any], 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any]= None
    ) -> Mapping[str, Any]:
        """
        Set request headers
        """
        return {"Authorization": self._token}
    
    def string_to_datetime(self, date_string, format="%Y-%m-%dT%H:%M:%S%z") -> datetime:
        """
        Converts a date string to a datetime object.

        Parameters:
            date_string (str): The date string to convert.
            format (str): The format of the date string (default is ISO 8601 format).

        Returns:
            datetime: The datetime object.
        """
        try:
            return datetime.strptime(date_string, format)
        except ValueError as e:
            self.logger.error(f"Failed to parse date string: {date_string}. Error: {e}")
            return None 
        
# IncrementalStream
class InventoriesRmsStream(RakutenRmsBaseStream, CheckpointMixin):
    """
    Incremental Stream Class for Rakuten RMS API
    """

    def __init__(self, config: Mapping[str, Any], **kwargs: Any) -> None:
        self._name = "inventories"
        self._path = "bulk-get/range"
        self._data_field = "inventories"
        self._min_quantity = config["inventories_min_quantity"]
        self._max_quantity = config["inventories_step_interval"]
        self._upper_limit = config["inventories_max_quantity"]
        super().__init__(config, **kwargs)

    url_base = "https://api.rms.rakuten.co.jp/es/2.1/inventories/"
    state_converter = EpochValueConcurrentStreamStateConverter()
    cursor_field = "updated"
    cursor_value = None
    primary_key = ["manageNumber","variantId"]

    @property
    def state(self) -> Mapping[str, Any]:
        """1
        Retrieve the stream state.
        """
        if self.cursor_value:
            return {self.cursor_field: self.cursor_value}
        else:
            return {self.cursor_field: "2024-11-27T15:13:03+09:00" }

    @state.setter
    def state(self, value: Mapping[str, Any]):
        """
        Set the stream state. 
        """
        self.logger.info("Setting state: %s", value)  # デバッグログ
        if value and self.cursor_field in value:
            self.cursor_value = value[self.cursor_field]
        else:
            self.logger.warning("Received empty state or state without cursor field")
            # デフォルト値を設定するか、エラー処理を行う
            self.cursor_value = "2024-11-27T15:13:03+09:00"
        
    @property
    def name(self) -> str:
        """
        ストリームの名前を取得する。
        """
        return self._name

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        次のページのトークンを取得する。
        """
        return None

    # update state
    def get_updated_state(
        self, 
        current_stream_state: MutableMapping[str, Any], 
        latest_record: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """
        ストリームの状態を更新する。
        """
        try:
            latest_state_str = latest_record.get(self.cursor_field, None) if latest_record else None
            current_state_str = current_stream_state.get(self.cursor_field, None) if current_stream_state else None

            self.logger.debug(f"DEBUG: current_stream_state={current_stream_state}, current_state_str={current_state_str}, latest_state_str={latest_state_str}")  # デバッグログ

            # 最新のレコードに状態がない場合、現在の状態をそのまま返却
            if not latest_state_str:
                return current_stream_state

            # 最新の状態を解析
            latest_state = parse(latest_state_str)

            # 現在の状態を解析（存在する場合のみ）
            current_state = parse(current_state_str) if current_state_str else None

            # 状態を比較
            if current_state is None or latest_state > current_state:
                return {self.cursor_field: latest_state.strftime(_OUTGOING_DATETIME_FORMAT)}

            return current_stream_state

        except Exception as e:
            self.logger.error(f"Error while updating state: {e}, current_stream_state={current_stream_state}, latest_record={latest_record}")
            raise AirbyteTracedException(
                message="Invalid date format in stream state or latest record",
                internal_message=str(e),
                failure_type=FailureType.config_error,
            )

    def request_params(
        self, 
        stream_state: Mapping[str, Any], 
        stream_slice: Mapping[str, any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        リクエストパラメータを設定する。
        """
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["minQuantity"] = stream_slice["minQuantity"] if stream_slice else self._min_quantity
        params["maxQuantity"] = stream_slice["maxQuantity"] if stream_slice else self._max_quantity
        return params

    def _fetch_next_page(
        self,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        """
        次のページをフェッチする。
        """
        self.logger.debug("Fetching page with token: %s:%s:%s", stream_slice, stream_state, next_page_token)  # デバッグ
        request, response = super()._fetch_next_page(stream_slice, stream_state, next_page_token)
        if response.status_code == 200 and response.json().get(self._data_field):
            time.sleep(_INVENTORIES_REQUEST_INTERVAL_SECONDS)  # リクエスト間隔を設定
        else:
            time.sleep(_INVENTORIES_RATE_LIMIT) # レートリミットを設定
        return request, response

    def parse_response(
        self, 
        response: requests.Response, 
        **kwargs
    ) -> Iterable[Mapping]:
        """
        レスポンスを解析する。
        例）
        [
            "inventories": {
                xxxx 
            }
        ]
        
        """
        response_json = response.json()
        # 
        # エラーを取得、存在しない場合はからのリスト
        errors = response_json.get("errors", [])

        # エラーを確認し、GE0014をスキップ
        if errors:
            for error in errors:
                if (error.get("code") == "GE0014"):
                    self.logger.warning("Error GE0014 encountered: %s", error)
                    yield from {}  # GE0014の場合はスキップ
        else:
            inventories = response_json.get(self._data_field, [])
            if not inventories:
                self.logger.warning("No inventories found for the given request body: %s", response_json)
                return None
            # データを昇順に並び替え
            sorted_data = sorted(inventories, key=lambda x: x.get(self.cursor_field))
            self.cursor_value = sorted_data[-1].get(self.cursor_field)
            yield from sorted_data

    def stream_slices(
        self, 
        stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        ストリームのスライスを生成する。
        """

        current_min_quantity = stream_state.get("minQuantity", self._min_quantity ) if stream_state else self._min_quantity
        current_max_quantity = stream_state.get("maxQuantity", current_min_quantity + self._max_quantity - 1) if stream_state else current_min_quantity + self._max_quantity - 1

        self.logger.info("Initial min quantity: %s, Initial max quantity: %s", current_min_quantity, current_max_quantity)  # デバッグ

        while current_min_quantity < self._upper_limit:
            yield {"minQuantity": current_min_quantity, "maxQuantity": current_max_quantity}
    
            # 次の範囲を更新
            current_min_quantity = current_max_quantity + 1
            current_max_quantity = min(current_min_quantity + self._max_quantity - 1, self._upper_limit)
            
            self.logger.info(f"Next min quantity: {current_min_quantity}, Next max quantity: {current_max_quantity}")  # デバッグ

    @property
    def availability_strategy(self) -> Optional[AvailabilityStrategy]:
        """
        利用可能性の戦略を取得する。
        """
        return None

    @property
    def use_cache(self) -> bool:
        """
        キャッシュを使用するかどうかを取得する。
        """
        return True

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        APIのパスを取得する。
        """
        return self._path

class SearchPurchaseOrderRms(RakutenRmsBaseStream):
    """
    購入注文アイテムを検索するためのクラス。
    """
    def __init__(self, name: str, config: Mapping[str, Any], **kwargs: Any) -> None:
        self._name = name
        self._path = "purchaseItem/searchOrderItem/"
        self._primary_key = "orderNumber"
        self._request_pages = 1
        self._order_progress_list = [100, 200, 300, 400, 500, 600, 700, 800, 900]

        # 本来は2年前の日付を計算するが、テスト用に1年前の日付を計算（後で変えて）
        self.start_datetime = (now - timedelta(days=_START_DATE_DELTA_DAYS)).strftime("%Y-%m-%dT%H:%M:%S%z")
        self.end_datetime = (datetime.strptime(self.start_datetime, "%Y-%m-%dT%H:%M:%S%z") + timedelta(days=_DATE_RANGE)).strftime("%Y-%m-%dT%H:%M:%S%z")
        super().__init__(config, **kwargs)

    http_method = "POST"
    url_base = "https://api.rms.rakuten.co.jp/es/2.0/"
    state_converter = EpochValueConcurrentStreamStateConverter()

    @property
    def use_cache(self) -> bool:
        """
        キャッシュを使用するかどうかを取得する。
        """
        return True

    @property
    @abstractmethod
    def date_type(self) -> int:
        """
        日付タイプを取得する。
        """
        pass

    @property
    def name(self) -> str:
        """
        ストリームの名前を取得する。
        """
        return self._name

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        APIのパスを取得する。
        """
        return self._path

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        プライマリキーを取得する。
        """
        return self._primary_key

    def request_headers(
        self, 
        stream_state: Mapping[str, Any], 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any]= None
    ) -> Mapping[str, Any]:
        """
        独自のリクエストヘッダーを設定する。
        """
        headers = super().request_headers(stream_state, stream_slice, next_page_token)
        return { "Content-Type": "application/json; charset=utf-8", **headers }

    # Paginationがないため、next_page_tokenは空の辞書を返す
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        次のページのトークンを取得する。
        """
        response_json = response.json()
        model = response_json.get("PaginationResponseModel", {})
        requestPage = model.get("requestPage", 0)
        orderNumberList = response_json.get("orderNumberList", [])
        self.logger.debug(f"Next Page Token: {response_json}, requestPage: {requestPage}")
        if orderNumberList:  # orderNumberListが空でない場合
            return {"requestPage": requestPage + 1}
        return None
    
    def request_body_json(
        self, 
        stream_state: Mapping[str, Any], 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        
        self.logger.debug("stream_slice: %s", stream_slice)
        try:
            start_date_time = stream_slice.get("startDatetime", self.start_datetime) if stream_slice else self.start_datetime
            end_date_time = stream_slice.get("endDatetime", self.end_datetime) if stream_slice else self.end_datetime
            order_progress_list = self._order_progress_list
            self.logger.debug(f"SearchPurchaseOrderRms next_page_token: {next_page_token}")
            
            json_body = {
                "dateType": self.date_type,
                "startDatetime": start_date_time,
                "endDatetime": end_date_time,
                "orderProgressList": order_progress_list,
                "PaginationRequestModel": {
                    "requestRecordsAmount": _PAGE_SIZE,
                    "requestPage": next_page_token.get("requestPage", 1) if next_page_token else 1
                },
                "SortModel": {
                    "sortColumn": _SORT_COLUMN,
                    "sortDirection": _SORT_DIREDCTION
                }
            }
            
            self.logger.debug(f" json: {json_body}")
            return json_body
        
        except Exception as e:
            self.logger.error(f"Error while creating request body: {e}")
            raise AirbyteTracedException(
                message="Error while creating request body",
                internal_message=str(e),
                failure_type=FailureType.config_error,
            )
        
    def _fetch_next_page(
        self,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        """
        次のページをフェッチする。
        """
        self.logger.debug(f"Fetching page with token: {stream_slice}:{stream_state}:{next_page_token}")  # デバッグ
        request, response = super()._fetch_next_page(stream_slice, stream_state, next_page_token)
        time.sleep(1)  # 1秒間隔でリクエストする必要があるみたい
        return request, response
    
    def stream_slices(
        self, 
        sync_mode, 
        cursor_field: List[str] = None, 
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        63日間隔で購入注文アイテムを検索するためのスライスを生成する。
        """
        # 現在の日付を取得
        now = datetime.now(timezone(timedelta(hours=9)))  # 日本のタイムゾーン (+0900)
        # 2年前の日付を計算
        self.start_datetime = stream_state.get("startDatetime", (now - timedelta(days=_START_DATE_DELTA_DAYS)).strftime("%Y-%m-%dT%H:%M:%S%z")) if stream_state else self.start_datetime
        self.end_datetime = stream_state.get("endDatetime", (datetime.strptime(self.start_datetime, "%Y-%m-%dT%H:%M:%S%z") + timedelta(days=_DATE_RANGE)).strftime("%Y-%m-%dT%H:%M:%S%z")) if stream_state else self.end_datetime

        while datetime.strptime(self.start_datetime, "%Y-%m-%dT%H:%M:%S%z") < now:
            self.logger.info(f"Start Date Time: {self.start_datetime}, End Date Time: {self.end_datetime}")
            yield { 
                "startDatetime": self.start_datetime, 
                "endDatetime": self.end_datetime,
            }
            # 次の期間を設定
            self.start_datetime = (datetime.strptime(self.end_datetime, "%Y-%m-%dT%H:%M:%S%z") + timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%S%z")
            self.end_datetime = (datetime.strptime(self.start_datetime, "%Y-%m-%dT%H:%M:%S%z") + timedelta(days=_DATE_RANGE)).strftime("%Y-%m-%dT%H:%M:%S%z")
            if datetime.strptime(self.end_datetime, "%Y-%m-%dT%H:%M:%S%z") > now:
                self.end_datetime = now.strftime("%Y-%m-%dT%H:%M:%S%z")

    def parse_response(
        self, 
        response: requests.Response, 
        stream_slice: Optional[Mapping[str, Any]], 
        **kwargs
    ) -> Iterable[Mapping]:
        response_json = response.json()
        pagination_info = response_json.get("PaginationResponseModel", {})
        self.logger.debug(f"Pagination Info: {pagination_info}")
        order_number_list = response_json.get("orderNumberList", [])
        self.logger.debug(f"Response JSON: {order_number_list}")
        for order_number in order_number_list:
            yield {"orderNumber": order_number}
            

class SearchPurchaseOrderItemRmsByOrderDate(SearchPurchaseOrderRms):
    def __init__(self, config: Mapping[str, Any], **kwargs: Any) -> None:
        super().__init__("purchase_order_items_order_date", config, **kwargs)

    date_type = 1 # 注文日時検索条件に設定する

# Items API
class RakutenRmsSubBaseStream(HttpSubStream, ABC):
    """
    楽天RMS-APIのサブストリーム基底クラス
    """
    def __init__(self, 
                 parent: Stream,
                 config: Mapping[str, Any], **kwargs: Any) -> None:
        self._token = generate_access_token(config["service_secret"], config["licence_key"])
        super().__init__(parent=parent, **kwargs)
        
    primary_key: Optional[Union[str, List[str], List[List[str]]]] = None
        
    def request_headers(
        self, 
        stream_state: Mapping[str, Any], 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any]= None
    ) -> Mapping[str, Any]:
        """
        リクエストヘッダーを設定する。
        """
        return {"Authorization": self._token}
    
    def get_error_handler(self) -> ErrorHandler:

        error_mapping = PARENT_INCREMENTAL_RMS_STREAM_ERROR_MAPPING

        return HttpStatusErrorHandler(logger=self.logger, error_mapping=error_mapping, max_retries=self.max_retries)

class CategoryMappingStream(RakutenRmsSubBaseStream):
    
    def __init__(self, parent_stream: Stream, config: Mapping[str, Any], **kwargs: Any) -> None:
        self._name = "category_mapping"
        self._primary_key = "categoryId"
        self._parent_stream = parent_stream
        self._processed_manage_numbers = set()
        super().__init__(parent=parent_stream, config=config, **kwargs)

    url_base = "https://api.rms.rakuten.co.jp/es/2.0/categories/"

    @property
    def name(self) -> str:
        return self._name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> Iterable[Mapping]:
        data = response.json()
        self.logger.info(f"response: {data}")
        manage_number = data.get("manageNumber")
        categories = data.get("categories", [])
        for category in categories:
            category["manageNumber"] = manage_number
            yield category

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        リクエストパラメータを設定する。
        """
        params = {}
        params["breadcrumb"] = "true"  # パンくずリストを取得する
        return params

    def next_page_token(
        self,
        response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self, 
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None
    ) -> str:
        """
        APIのパスを取得する。
        """
        try:
            path_str = f"item-mappings/manage-numbers/{stream_slice['manageNumber']}"
            return path_str
        except KeyError as e:
            raise
        except Exception as e:
            raise

    def _fetch_next_page(
        self,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        self.logger.debug(f"Fetching page with token: {stream_slice}:{stream_state}:{next_page_token}")  # デバッグ
        request, response = super()._fetch_next_page(stream_slice, stream_state, next_page_token)
        time.sleep(_CATEGORIES_REQUEST_INTERVAL_SECONDS)  # リクエスト間隔を設定
        return request, response
        
    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        ストリームのスライスを生成する。
        """
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state
        )
        
        # iterate over parent stream slices
        for stream_slice in parent_stream_slices:
            self.logger.debug(f"Parent stream slice: {stream_slice}")
            parent_records = self.parent.read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
            # iterate over all parent records with current stream_slice
            for record in parent_records:
                manage_number = record.get("manageNumber")
                if manage_number in self._processed_manage_numbers:
                    self.logger.debug(f"Skipping already processed manageNumber: {manage_number}")  # デバッグログ
                    continue
                self._processed_manage_numbers.add(manage_number)
                self.logger.debug(f"Parent sub record: {record}")
                yield record

class CategoryTreeStream(RakutenRmsBaseStream):

    def __init__(
        self,
        config: Mapping[str, Any],
        **kwargs: Any
    ) ->None:
        self._name = "category_relation_report"
        self._path = "shop-category-trees/category-set-ids/0"
        self._primary_key = "categoryId"
        super().__init__(config, **kwargs)
    
    url_base = "https://api.rms.rakuten.co.jp/es/2.0/categories/"
    state_converter = EpochValueConcurrentStreamStateConverter()

    @property
    def name(self) -> str:
        return self._name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        プライマリキーを取得する。
        """
        return self._primary_key

    def parse_response(
        self, 
        response: requests.Response, 
        **kwargs
    ) -> Iterable[Mapping]:
        
        data = response.json()
        self.logger.info(f"response: {data}")

        # rootNodeの取得、デフォルトは空の辞書
        root = data.get("rootNode", {})
        # 最上位のchildrenリストを取得
        children = root.get("children", [])

        for child in children:
            
            params = {}
            category = child.get("category")
            params["categorySetId"] = category.get("categorySetId")
            params["categoryId"] = category.get("categoryId")
            params["title"] = category.get("title")
            params["layout"] = category.get("layout", {})
            params["created"] = category.get("created")
            params["updated"] = category.get("updated")
            params["children"] = child.get("children", [])
            yield params

    def path(
        self, 
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None
    ) -> str:
        """
        APIのパスを取得する。
        """
        return self._path
    
    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from [{}]  # スライスを生成する   
        
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        リクエストパラメータを設定する。
        """
        params = {}
        params["categorysetfields"] = "TITLE,CATEGORY_SET_FEATURES,CREATED,UPDATED" # 複数指定でカンマ区切り
        params["categoryfields"] = "CATEGORY_SET_ID,TITLE,DESCRIPTION,IMAGES,LAYOUT,CREATED,UPDATED" # 複数指定でカンマ区切り
        return params
        
        
class CategoryStream(RakutenRmsBaseStream):
    
    def __init__(
        self,
        config: Mapping[str, Any],
        **kwargs: Any
    ) ->None:
        self._name = "category_set_lists"
        self._path = "shop-category-set-lists"
        self._primary_key = "categorySetId"
        super().__init__(config, **kwargs)
        
    url_base = "https://api.rms.rakuten.co.jp/es/2.0/categories/"
    state_converter = EpochValueConcurrentStreamStateConverter()
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        プライマリキーを取得する。
        """
        return self._primary_key
    
    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        APIのパスを取得する。
        """
        return self._path
    
    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from [{}]  # スライスを生成する   
        
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        リクエストパラメータを設定する。
        """
        return { 
            "categorysetfields" : "TITLE,CATEGORY_SET_FEATURES,CREATED,UPDATED", # 複数指定でカンマ区切り
        }
    
    def parse_response(
        self, 
        response: requests.Response, 
        **kwargs
    ) -> Iterable[Mapping]:
        """
        レスポンスを解析する。
        """
        data = response.json()
        categories = data.get("categorySetList", [])
        self.logger.info(f"Response JSON: {categories}")
        yield from categories

class BundleStream(RakutenRmsBaseStream):
    """
    BundleStreamのAPIを取得するためのクラス
    """
    def __init__(
        self, 
        config: Mapping[str, Any], 
        **kwargs: Any
    ) -> None:
        self._name = "bundles"
        self._path = "bundles"
        self._primary_key = "bundleId"
        super().__init__(config, **kwargs)
        
    url_base = "https://api.rms.rakuten.co.jp/es/1.0/bto/"
    primary_key = "bundleManageNumber"
    state_converter = EpochValueConcurrentStreamStateConverter()

    @property
    def availability_strategy(self) -> Optional[AvailabilityStrategy]:
        return None
    
    @property
    def name(self) -> str:
        """
        ストリームの名前を取得する。
        """
        return self._name
        
    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 404:
            # 404エラーの場合はリトライをせずに空のストリームとして処理
            return False
        # その他のケースはデフォルトの動作を維持
        return super().should_retry(response)

    def parse_response(
        self, 
        response: requests.Response, 
        **kwargs
    ) -> Iterable[Mapping]:
        """
        レスポンスを解析する。
        """
        errors = response.json().get("errors", [])
        if errors:
            return [] # 404エラーの場合は空のリストを返す
        data = response.json()
        bundles = data.get("bundles", [])
        yield from bundles

    def request_headers(
        self, 
        stream_state: Mapping[str, Any], 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any]= None
    ) -> Mapping[str, Any]:
    
        headers = super().request_headers(stream_state, stream_slice, next_page_token)
        return { "Content-Type": "application/json; charset=utf-8", **headers }

    def path(
        self, 
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None
    ) -> str:
        """
        APIのパスを取得する。
        """
        return self._path
    
    
    # Paginationがないため、next_page_tokenは空の辞書を返す
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        次のページのトークンを取得する。
        """
        return {}
    
# class BulkGetItemsSubStream(RakutenRmsSubBaseStream):
    
#     def __init__(self, parent_stream: Stream, config: Mapping[str, Any], **kwargs: Any) -> None:
#         self._name = "items"
#         self._primary_key = [["manageNumber","itemNumber"]]
#         self._path = "bulk-get"
#         super().__init__(parent_stream, config, **kwargs)

#     url_base = "https://api.rms.rakuten.co.jp/"
#     state_converter = EpochValueConcurrentStreamStateConverter()
    
#     def path(
#         self,
#         *,
#         stream_state: Optional[Mapping[str, Any]] = None,
#         stream_slice: Optional[Mapping[str, Any]] = None,
#         next_page_token: Optional[Mapping[str, Any]] = None,
#     ) -> str:
#         """
#         APIのパスを取得する。
#         """
#         return self._path
        
#     def next_page_token():
#         """
#         次のページのトークンを取得する。
#         """
#         return None
    
#     def request_body_json(self, 
#                           stream_state, 
#                           stream_slice = None, 
#                           next_page_token = None) -> Optional[Mapping[str, Any]]:
#         json_body = {
#             "manageNumbers": [stream_slice["manageNumber"]],
#         }
#         return json_body
    
class PurchaseOrderTaxSummaryModel(Stream):
    
    def __init__(self, parent_stream: Stream, config: Mapping[str, Any], **kwargs: Any) -> None:
        self._name = "purchase_order_tax_summary"
        self._primary_key = "order"
        
    @property
    def name(self) -> str:
        return self._name
        
    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        self._primary_key
        
    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        """
        レコードを読み込む。
        この関数では、APIは実行しない
        """
        pass

class PurchaseOrderPackageModelStream(Stream):
    
    def __init__(self, parent_stream: Stream, config: Mapping[str, Any], **kwargs: Any) -> None:
        self._name = "purchase_order_package_model"
        self._primary_key = "basketId"
        self._parent_stream = parent_stream

    @property
    def name(self) -> str:
        return self._name
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return {}

    def parse_response(
        self, 
        response, 
        *, 
        stream_state, 
        stream_slice = None, 
        next_page_token = None
    ) -> Iterable[Mapping[str, Any]]:
        return response.json()

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key
        
    def read_records(
        self,
        sync_mode: SyncMode, 
        cursor_field: List[str] = None, 
        stream_slice: Mapping[str, Any] = None, 
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Mapping[str, Any]]:
        """
        レコードを読み込む。
        この関数では、APIは実行しない
        """

        for child_slice in self._parent_stream.stream_slices(stream_state=stream_state):
            for parent_record in self._parent_stream.read_records(sync_mode, cursor_field, stream_slice=child_slice, stream_state=stream_state):
                if 'PackageModelList' in parent_record:
                    for sub_item in parent_record['PackageModelList']:
                        yield {
                            "orderNumber": parent_record["orderNumber"],
                            "basketId": sub_item["basketId"],
                            "postagePrice": sub_item["postagePrice"],
                            "deliveryPrice": sub_item["deliveryPrice"],
                            "deliveryTaxRate": sub_item["deliveryTaxRate"],
                            "goodsPrice": sub_item["goodsPrice"],
                            "totalPrice": sub_item["totalPrice"],
                            "defaultDeliveryCompanyCode": sub_item["defaultDeliveryCompanyCode"],
                            # その他の必要なフィールド
                        }

class PurchaseOrderItemsStream(RakutenRmsSubBaseStream): 
    """
    購入注文アイテムを取得するためのクラス。
    """
    def __init__(self, parent_stream: Stream, config: Mapping[str, Any], **kwargs: Any) -> None:
        self._name = "purchase_order"
        self._path = "purchaseItem/getOrderItem"
        self._primary_key = "orderNumber"
        self._order_number_list = []
        self._parent_stream = parent_stream

         # 本来は2年前の日付を計算するが、テスト用に1年前の日付を計算（後で変えて）
        self.start_datetime = (now - timedelta(days=_START_DATE_DELTA_DAYS)).strftime("%Y-%m-%dT%H:%M:%S%z")
        self.end_datetime = (datetime.strptime(self.start_datetime, "%Y-%m-%dT%H:%M:%S%z") + timedelta(days=_DATE_RANGE)).strftime("%Y-%m-%dT%H:%M:%S%z")

        super().__init__(parent=parent_stream, config=config, **kwargs)
        
    http_method = "POST"
    url_base = "https://api.rms.rakuten.co.jp/es/2.0/"
    state_converter = EpochValueConcurrentStreamStateConverter()

    @property
    def name(self) -> str:
        """
        ストリームの名前を取得する。
        """
        return self._name
    
    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        APIのパスを取得する。
        """
        return self._path
    
    # @property
    # def use_cache(self) -> bool:
    #     return True

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        プライマリキーを取得する。
        """
        return self._primary_key
    
    # Paginationがないため、next_page_tokenは空の辞書を返す
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None
    
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(sync_mode=sync_mode, stream_slice=stream_slice, stream_state=stream_state):
            self.logger.debug(f"Reading record: {record}")  # デバッグログ
            yield record
        
    def request_body_json(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        """
        Example: 
        {
            "orderNumberList": [
                "123456-20230101-0000000001",
                "123456-20230101-0000000002",
                "123456-20230101-0000000003"
            ]
        } 
        """
        self.logger.debug(f"GetPurchaseDetails: stream_slice: {stream_slice}, stream_state: {stream_state}, next_page_token: {next_page_token}")
        order_number = stream_slice.get("orderNumberList")
        body = {"orderNumberList": order_number}
        self.logger.debug("body %s", body)
        return body
    
    # APIのリクエスト間隔を設定する
    # 404が発生したときに、この関数内で、エラーになるので、エラーにならないようにNoneを返す
    def _fetch_next_page(
        self,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        """
        次のページをフェッチする。
        """
        self.logger.debug(f"GetPurchaseDetails: Fetching page with token: {stream_slice}:{stream_state}:{next_page_token}")  # デバッグ
        request, response = super()._fetch_next_page(stream_slice, stream_state, next_page_token)
        time.sleep(_PURCHASE_ITEM_REQUEST_INTERVAL_SECONDS)  # リクエスト間隔を設定
        return request, response
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json.get("OrderModelList", [])
        self.logger.debug(f"Number of records parsed: {len(records)}")
        yield from records
    
    def request_headers(
        self, 
        stream_state: Mapping[str, Any], 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any]= None
    ) -> Mapping[str, Any]:
        """
        独自のリクエストヘッダーを設定する。
        """
        headers = super().request_headers(stream_state, stream_slice, next_page_token)
        return { "Content-Type": "application/json; charset=utf-8", **headers }
    
    def stream_slices(
        self, stream_state: Mapping[str, Any] = None, 
        **kwargs
    ) -> Iterable[Optional[Mapping[str, Any]]]:
    
        """
        ストリームのスライスを生成する。
        """
        order_numbers = []
        parent_stream_slices = super().stream_slices(sync_mode=SyncMode.full_refresh)
        for _slice in parent_stream_slices:
            self.logger.debug(f"GetPurchaseDetails: Parent stream slice: {_slice}")
            order_number = _slice["parent"]["orderNumber"]
            order_numbers.append(order_number)
            if len(order_numbers) >= 100:  # APIの制限に応じて調整
                yield {"orderNumberList": order_numbers}
                order_numbers = []
        if order_numbers:
            yield {"orderNumberList": order_numbers}
        else:
            yield None

class ItemVariantsRmsSubStream(Stream):
    """
    
    """
    def __init__(self, parent_stream: Stream, config: Mapping[str, Any], **kwargs: Any) -> None:
        self._name = "items_sku_report"
        self._primary_key = ["manageNumber", "variantId"]
        self._parent_stream = parent_stream
        
    @property
    def name(self) -> str:
        return self._name
    
    def parse_response(
        self, 
        response, 
        *, 
        stream_state, 
        stream_slice = None, 
        next_page_token = None
    ) -> Iterable[Mapping[str, Any]]:
        return response.json()

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    def read_records(
        self, 
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None, 
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        レコードを読み込む。
        この関数では、APIは実行しない
        """

        for child_slice in self._parent_stream.stream_slices(stream_state=stream_state):
            self.logger.info(f"ItemVariantsRmsSubStream: Child Slice: {child_slice}")
            for parent_record in self._parent_stream.read_records(sync_mode=sync_mode, stream_slice=child_slice, cursor_field=cursor_field, stream_state=stream_state):
                self.logger.info(f"Parent Record: {parent_record}")
                variants = parent_record.get('variants', {})
                manage_number = parent_record.get('manageNumber')
                self.logger.info(f"Parent Record: {parent_record}")
                for key, value in variants.items():
                    yield { "manageNumber": manage_number, "variantId": key, **value }
                        

class GetItemsRmsSubStream(RakutenRmsSubBaseStream):
    """
    inventoriesのmanageNumberのデータをパスパラメータにして、サブストリームを取得するためのクラス。
    """
    def __init__(self, parent_stream: Stream, config: Mapping[str, Any], **kwargs: Any) -> None:
        self._name = "items"
        # self._primary_key = ["manageNumber","itemNumber"]
        # self._processed_manage_numbers = set()
        self._parent_stream = parent_stream
        super().__init__(parent_stream, config, **kwargs)
                 
    url_base = "https://api.rms.rakuten.co.jp/"
    primary_key = ["manageNumber", "itemNumber"]
    
    @property
    def use_cache(self) -> bool:
        return True

    # Paginationがないため、next_page_tokenは空の辞書を返す
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        次のページのトークンを取得する。
        """
        # self.logger.debug(f"Next page token: {self._parent_stream}")
        # return { "manageNumber": "wb25_collab" }
        # self._parent_stream.read_records(sync_mode=SyncMode.full_refresh)
        return {}
    
    # APIのリクエスト間隔を設定する
    # 404が発生したときに、この関数内で、エラーになるので、エラーにならないようにNoneを返す
    def _fetch_next_page(
        self,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        """
        次のページをフェッチする。
        """
        try:
            self.logger.debug(f"Fetching page with token: {stream_slice}:{stream_state}:{next_page_token}")  # デバッグ
            request, response = super()._fetch_next_page(stream_slice, stream_state, next_page_token)
            time.sleep(_ITEMS_REQUEST_INTERVAL_SECONDS)  # リクエスト間隔を設定
            return request, response
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 404:
                self.logger.warning(f"404 error encountered: {http_err}")
                return None, None
            else:
                raise
        
    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        リクエストパラメータを設定する。
        """
        return None
    
    def request_headers(
        self, 
        stream_state: Mapping[str, Any], 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any]= None
    ) -> Mapping[str, Any]:
        """
        リクエストヘッダーを設定する。
        """
        return {"Authorization": self._token}
        
    def parse_response(
        self, 
        response: requests.Response, 
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Mapping]:
        """
        レスポンスを解析する。
        """
        try:
            
            if response is None:
                self.logger.warning("No response found.")
                return
            
            # レスポンスをJSONとして解析
            response_json = response.json()

            # 正常レスポンスのログを記録
            self.logger.debug(f"Response JSON: {response_json}")

            # レスポンスからデータを抽出して返す
            data = response_json.get("manageNumber", [])
            if not data:
                self.logger.warning("No data found in response.")
            yield response_json # データがない場合は空のリストを返す

        except ValueError as e:
            # 例外のログを記録
            self.logger.error(f"Failed to parse response: {response.text}. Error: {e}")
            raise

    @property
    def name(self) -> str:
        """
        ストリームの名前を取得する。
        """
        return self._name
        
    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        APIのパスを取得する。
        """
        try:
            self.logger.debug(f"Using stream_slice in path: {stream_slice}:{stream_state}:{next_page_token}")  # デバッグログ
            path_str = f"/es/2.0/items/manage-numbers/{stream_slice['manageNumber']}"
            self.logger.debug("Path: %s", path_str)  # デバッグログ
            return path_str
            # return self._path.format(stream_slice=stream_slice)
        except KeyError as e:
            self.logger.error(f"Missing key in stream_slice for path formatting: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error formatting path with stream_slice: {stream_slice}. Erorr: {e}")
            raise
    
    def read_records(
        self, 
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        レコードを読み取る。
        """
        for record in super().read_records(sync_mode=sync_mode, stream_slice=stream_slice, stream_state=stream_state):
            self.logger.debug(f"Reading record: {record}")  # デバッグログ
            yield record
    
    def stream_slices(
        self, 
        stream_state: Mapping[str, Any] = None,
        **kwargs
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        ストリームのスライスを生成する。
        """
        #parent_stream_slices = self.parent.stream_slices(
        #    sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        #)
        processed_manage_numbers = set()
        parent_stream_slices = self._parent_stream.stream_slices(sync_mode=SyncMode.full_refresh, stream_state=stream_state)
        
        # iterate over parent stream slices
        for stream_slice in parent_stream_slices:
            self.logger.debug(f"Parent stream slice: {stream_slice}")
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, stream_state=stream_state
            )
            # iterate over all parent records with current stream_slice
            for record in parent_records:
                manage_number = record.get("manageNumber")
                if manage_number in processed_manage_numbers:
                    self.logger.debug(f"Skipping already processed manageNumber: {manage_number}")  # デバッグログ
                    continue
                processed_manage_numbers.add(manage_number)
                self.logger.debug(f"Parent sub record: {record}")
                yield record

class NavigationRmsStream(RakutenRmsBaseStream):
    """
    ナビゲーションAPIの基底クラス。
    """
    def __init__(self,
                 name: str,
                 path: str,
                 primary_key: Union[str, List[str]],
                 config: Mapping[str, Any],
                 **kwargs: Any) -> None:
        self._name = name
        self._path = path   
        self._primary_key = primary_key
        super().__init__(config, **kwargs)

    url_base = "https://api.rms.rakuten.co.jp/es/2.0/navigation/"

    @property
    def name(self) -> str:
        """
        ストリームの名前を取得する。
        """
        return self._name

    def path(
            self,
            *,
            stream_state: Optional[Mapping[str, Any]] = None,
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
        ) -> str:
        """
        APIのパスを取得する。
        """
        return self._path
    
    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        プライマリキーを取得する。
        """
        return self._primary_key
    
    def string_to_datetime(self, date_string, format="%Y-%m-%dT%H:%M:%S%z") -> datetime:
        """
        日付文字列をdatetimeオブジェクトに変換します。

        パラメータ:
            date_string (str): 変換する日付文字列。
            format (str): 日付文字列の形式（デフォルトはISO 8601形式）。

        戻り値:
            datetime: datetimeオブジェクト。
        """
        try:
            return datetime.strptime(date_string, format)
        except ValueError as e:
            self.logger.error(f"Failed to parse date string: {date_string}. Error: {e}")
            return None 

class GetChildrenGenreStream(RakutenRmsSubBaseStream):
    """
    子ジャンルを取得するためのクラス。
    """

    def __init__(
        self,
        parent_stream: Stream,
        config: Mapping[str, Any],
        **kwargs: Any
    ) -> None:
        self._name = "genres_children"
        super().__init__(parent_stream, config, **kwargs)
        
    primary_key = "genreId"
    url_base = "https://api.rms.rakuten.co.jp/"
    state_converter = EpochValueConcurrentStreamStateConverter()

    @property
    def name(self) -> str:
        return self._name

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        APIのパスを取得する。
        """
        try:
            self.logger.debug(f"Using stream_slice in path")
            path_str = f"/es/2.0/navigation/genres/{stream_slice['genreId']}"
            return path_str
        except KeyError as e:
            raise
        except Exception as e:
            raise

    def read_records(
        self, 
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        レコードを読み取る。
        """
        for record in super().read_records(sync_mode=sync_mode, stream_slice=stream_slice, stream_state=stream_state):
            self.logger.debug(f"Reading record: {record}")  # デバッグログ
            yield record

    def request_params(
        self, 
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {}
        params['showAncestors'] = 'true'
        params['showSiblings'] = 'true'
        params['showChildren'] = 'true'
        return params

    def next_page_token(
        self, 
        response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        """
        次のページのトークンを取得する。
        """
        return None

    def stream_slices(
        self, 
        sync_mode: SyncMode, 
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        
        parent_stream_slices = super().stream_slices(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state
            )

        # iterate over parent stream slices
        for stream_slice in parent_stream_slices:
            self.logger.debug(f"Parent stream slice: {stream_slice}")
            parent_records = self.parent.read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
            # iterate over all parent records with current stream_slice
            for record in parent_records:
                self.logger.debug(f"Parent sub record: {record}")
                yield record
    
    def _fetch_next_page(
        self,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        request, response = super()._fetch_next_page(stream_slice, stream_state, next_page_token)
        time.sleep(1) # レートリミットを設定
        return request, response

    def parse_response(
        self, 
        response: requests.Response, 
        **kwargs
    ) -> Iterable[Mapping]:
        """
        レスポンスを解析する。
        """
        response_json = response.json() 
        genre = response_json.get("genre")
        self.logger.info(f"genre is response: {response_json}")
        yield genre

class GetParentGenreStream(NavigationRmsStream):
    """
    親ジャンルを取得するためのクラス。
    """

    def __init__(self, config: Mapping[str, Any]) -> None:
        super().__init__(
            name="genres", 
            path="genres/0", 
            primary_key="genreId", 
            config=config)

    data_field = "genre"
    state_converter = EpochValueConcurrentStreamStateConverter()

    def next_page_token(self, response):
        """
        次のページのトークンを取得する。
        """
        return None
    
    def parse_response(
        self, 
        response: requests.Response, 
        **kwargs
    ) -> Iterable[Mapping]:
        """
        レスポンスを解析する。
        以下がレスポンス例
        {
            "version": {
                "id": 60,
                "fixedAt": "2024-11-20T08:17:07+09:00"
            },
            "genre": {
                children: [
                    {
                        "genreId": 12345,
                        "genreIdPath": [
                            12345
                        ],
                        "nameJa": "メンズファッション",
                        "nameJaPath": [
                            "メンズファッション"
                        ],
                        "level": 1,
                        "lowest": false,
                        "properties": {
                            "itemRegisterFlg": false
                        },
                        "ancestors": null,
                        "siblings": null,
                        "children": null
                    },
                    ......
                ]
            }
        }

        """
        if response is None:
                self.logger.warning("No response found.")
                return
        response_json = response.json()
        genre = response_json.get(self.data_field, [])
        self.logger.info(f"genre is response: {response_json}")
        for child in genre.get("children", []):
            yield child
        
class GetVersionStream(NavigationRmsStream, CheckpointMixin):
    """
    バージョン情報を取得するためのクラス。
    """

    def __init__(
        self,
        config: Mapping[str, Any]
    ) -> None:   
        super().__init__(
            name="version", 
            path="version", 
            primary_key="id", 
            config=config)
        self._cursor_value = None

    data_field = "version"
    cursor_field = "fixedAt"
    state_converter = IsoMillisConcurrentStreamStateConverter()

    @property
    def state(self) -> Mapping[str, Any]:
        return { self.cursor_field: self._cursor_value } if self._cursor_value else None
    
    @state.setter
    def state(self, value: Mapping[str, Any]):
        self.logger.info("Setting state: %s", value)  # デバッグログ
        self._cursor_value = value.get(self.cursor_field, None) if value else None

    def request_headers(
        self, 
        stream_state: Mapping[str, Any], 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any]= None
    ) -> Mapping[str, Any]:
        """
        リクエストヘッダーを設定する。
        """
        headers = super().request_headers(stream_state, stream_slice, next_page_token)
        return { "Content-Type": "application/json; charset=utf-8", **headers }

    def get_updated_state(
        self, 
        current_stream_state: MutableMapping[str, Any], 
        latest_record: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """
        ストリームの状態を更新する。
        """
        
        latest_state_value = self.string_to_datetime(latest_record.get(self.cursor_field))
        current_state_value = self.string_to_datetime(current_stream_state.get(self.cursor_field)) if current_stream_state else None
        self.logger.info("Current state value: %s, Latest state value: %s", current_state_value, latest_state_value)
        state_value = max(current_state_value, latest_state_value) if current_state_value else latest_state_value
        return { self.cursor_field: state_value }

    def _fetch_next_page(
        self,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        """
        次のページをフェッチする。
        """
        self.logger.debug(f"Fetching page with token: {stream_slice}:{stream_state}:{next_page_token}")  # デバッグ
        request, response = super()._fetch_next_page(stream_slice, stream_state, next_page_token)
        time.sleep(1)  # リクエスト間隔を設定
        return request, response

    def next_page_token(self, response):
        """
        次のページのトークンを取得する。
        """
        return None
    
    def read_records(self, 
                     sync_mode: SyncMode,
                     cursor_field: List[str] = None,
                     stream_slice: Optional[Mapping[str, Any]] = None,
                     stream_state: Mapping[str, Any] = None,
                     ) -> Iterable[Mapping[str, Any]]:
        """
        レコードを読み取る。
        """
        for record in super().read_records(sync_mode=sync_mode, stream_slice=stream_slice, stream_state=stream_state):
            self.logger.info(f"Reading record Version: {record}")  # デバッグログ
            yield record

    def parse_response(
        self, 
        response: requests.Response, 
        **kwargs
    ) -> Iterable[Mapping]:
        """
        レスポンスを解析する。
        以下がレスポンス例
        {
            "version": {
                "id": 60,
                "fixedAt": "2024-11-20T08:17:07+09:00"
            }
        }
        """
        response_json = response.json()
        self.logger.info(f"Response JSON: {response_json}")
        yield response_json.get(self.data_field, {})


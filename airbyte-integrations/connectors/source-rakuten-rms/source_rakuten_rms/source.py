#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from logging import Logger
import sys
from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.declarative.async_job.job_tracker import JobTracker
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import EpochValueConcurrentStreamStateConverter
import pendulum
from datetime import datetime
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk.logger import AirbyteLogFormatter
from airbyte_cdk.models import (
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    Level,
    SyncMode,
)
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor, CursorField, FinalStateCursor
from datetime import datetime

from .streams import (
    CategoryMappingStream,
    CategoryStream,
    PurchaseOrderItemsStream,
    InventoriesRmsStream,
    GetVersionStream,
    GetParentGenreStream,
    GetItemsRmsSubStream,
    SearchPurchaseOrderItemRmsByOrderDate,
    BundleStream,
    CategoryTreeStream,
    GetChildrenGenreStream,
    PurchaseOrderPackageModelStream,
    ItemVariantsRmsSubStream,
)

# 
_START_DATE = datetime(2020,1,1, 0,0,0).timestamp() 
_DEFAULT_CONCURRENCY = 10
_MAX_CONCURRENCY = 10
logger = logging.getLogger("airbyte")

class SourceRakutenRms(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None
    
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        inventories = InventoriesRmsStream(config)
        version = GetVersionStream(config)
        genres = GetParentGenreStream(config)
        genres_child = GetChildrenGenreStream(genres, config)
        items = GetItemsRmsSubStream(inventories, config)
        purchase_order_items_order_date_parent = SearchPurchaseOrderItemRmsByOrderDate(config)
        purchase_order_items_order_date = PurchaseOrderItemsStream(purchase_order_items_order_date_parent, config)
        purchase_order_package_model = PurchaseOrderPackageModelStream(purchase_order_items_order_date, config)
        bundles = BundleStream(config)
        categories = CategoryStream(config)
        catetory_tree = CategoryTreeStream(config)
        category_mapping = CategoryMappingStream(inventories, config)
        items_sku_report = ItemVariantsRmsSubStream(items, config)
        
        return [
            inventories,
            version,
            genres,
            genres_child,
            items,
            bundles,
            purchase_order_items_order_date,
            categories,
            catetory_tree,
            category_mapping,
            items_sku_report,
            purchase_order_package_model,
        ]


# # 並列動かすとページネーションが動かなくなるので、シングルスレッドでいったん実装
# class SourceRakutenRms1(ConcurrentSourceAdapter):

#     DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
#     START_DATE_OFFSET_IN_YEARS = 2
#     stop_sync_on_stream_failure = True
#     MAX_WORKERS = 5
#     message_repository = InMemoryMessageRepository(Level(AirbyteLogFormatter.level_mapping[logger.level]))

#     def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: Optional[Mapping[str, Any]], **kwargs):
#         if config:
#             concurrency_level = min(config.get("num_workers", _DEFAULT_CONCURRENCY), _MAX_CONCURRENCY)
#         else:
#             concurrency_level = _DEFAULT_CONCURRENCY
#         logger.info(f"Using concurrent cdk with concurrency level {concurrency_level}")
#         concurrent_source = ConcurrentSource.create(
#             concurrency_level, concurrency_level // 2, logger, self._slice_logger, self.message_repository
#         )
#         super().__init__(concurrent_source)
#         self.catalog = catalog
#         self._config = config
#         self._state = state
#         self._job_tracker = JobTracker(limit=5)

#     @staticmethod
#     def _get_rms_object(config: Mapping[str, Any]):
#         pass

#     def _validate_stream_slice_step(stream_slice_step: str) -> None:
#         pass

#     # チュートリアル通りに実装しているため、修正必要
#     def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
#         first_stream = next(iter(self.streams(config)))
#         stream_slice = next(iter(first_stream.stream_slices(sync_mode=SyncMode.full_refresh)))
#         try:
#             read_stream = first_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
#             first_record = None
#             while not first_record:
#                 first_record = next(read_stream)
#                 if isinstance(first_record, AirbyteMessage) and first_record.type == "RECORD":
#                     return True, None
#             return True, None
#         except Exception as e:
#             return False, f"Unable to connect to the API with the provided credentials - {str(e)}"

#     def _wrap_for_concurrency(self, config, stream, state_manager):
#         stream_slice_cursor = None
#         if stream.cursor_field:
#             pass
#         if hasattr(stream, "parent") and hasattr(stream.parent, "set_cursor"):
#             stream_slice_cursor = self._create_stream_slice_cursor(config, state_manager, stream)
#             stream.parent.set_cursor(stream_slice_cursor)

#         if not stream_slice_cursor or self._get_sync_mode_from_catalog(stream) == SyncMode.full_refresh:
#             cursor = FinalStateCursor(
#                 stream_name=stream.name, stream_namespace=stream.namespace, message_repository=self.message_repository
#             )
#             state = None
#         else:
#             cursor = stream_slice_cursor
#             state = cursor.state
#         return StreamFacade.create_from_stream(stream, self, logger, state, cursor)

#     def streams(self, config: Mapping[str, Any]) -> List[Stream]:
#         inventories = InventoriesRmsStream(config)
#         version = GetVersionStream(config)
#         genres = GetParentGenreStream(config)
#         items = GetItemsRmsSubStream(inventories, config)
#         purchase_order_items_order_date_parent = SearchPurchaseOrderItemRmsByOrderDate(config)
#         purchase_order_items_order_date = GetPurchaseOrderRmsStream(purchase_order_items_order_date_parent, config)
#         # purchase_order_package_model = GetPurchaseOrderPackageModelStream(purchase_order_items_order_date, config)
#         bundles = BundleStream(config)
#         categories = CategoryStream(config)
#         catetory_tree = CategoryTreeStream(config)
        
#         return [
#             inventories,
#             version,
#             genres,
#             items,
#             purchase_order_items_order_date,
#             # purchase_order_package_model,
#             bundles,
#             categories,
#             catetory_tree,
#         ]
    
#     """
#     #Rakuten RMSのデータソースクラス。
#     """

#     DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
#     START_DATE_OFFSET_IN_YEARS = 2
#     MAX_WORKERS = 5
#     stop_sync_on_stream_failure = True
#     message_repository = InMemoryMessageRepository(Level(AirbyteLogFormatter.level_mapping[logger.level]))
    
#     # def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: Optional[Mapping[str, Any]], **kwargs):
#     def __init__(self, config: Optional[Mapping[str, Any]], state: Optional[Mapping[str, Any]]):
#         if config:
#             concurrency_level = min(config.get("num_workers", _DEFAULT_CONCURRENCY), _MAX_CONCURRENCY)
#         else:
#             concurrency_level = _DEFAULT_CONCURRENCY
#         logger.info(f"Using concurrent cdk with concurrency level {concurrency_level}")
#         concurrent_source = ConcurrentSource.create(
#             concurrency_level, concurrency_level // 2, logger, self._slice_logger, self.message_repository
#         )
#         super().__init__(concurrent_source)
#         # self.catalog = catalog
#         self._config = config
#         self._state = state
#         # self._job_tracker = JobTracker(limit=5)

#     def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
#         """
#         #API接続をチェックする
#         """
#         first_stream = next(iter(self.streams(config)))
#         stream_slice = next(iter(first_stream.stream_slices(sync_mode=SyncMode.full_refresh)))
#         try:
#             read_stream = first_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
#             first_record = None
#             while not first_record:
#                 first_record = next(read_stream)
#                 if isinstance(first_record, AirbyteMessage) and first_record.type == "RECORD":
#                     return True, None
#             return True, None
#         except Exception as e:
#             return False, f"Unable to connect to the API with the provided credentials - {str(e)}"

#     def streams(self, config: Mapping[str, Any]) -> List[Stream]:
#         """
#         # 利用可能なストリームを取得する。
#         """
        
#         inventories = InventoriesRmsStream(config)
#         version = GetVersionStream(config)
#         genres = GetParentGenreStream(config)
#         items = GetItemsRmsSubStream(inventories, config)
#         purchase_order_items_order_date_parent = SearchPurchaseOrderItemRmsByOrderDate(config)
#         purchase_order_items_order_date = GetPurchaseOrderRmsStream(purchase_order_items_order_date_parent, config)
#         purchase_order_package_model = GetPurchaseOrderPackageModelStream(purchase_order_items_order_date, config)
#         bundles = BundleStream(config)
#         categories = CategoryStream(config)
#         catetory_tree = CategoryStream(config)
        
#         logger.info("primary_key %s %s", inventories.primary_key, type(inventories.primary_key))
        
#         synchronous_streams = [
#             inventories,
#             items,
#             version,
#             genres,
#             purchase_order_items_order_date_parent,
#             # purchase_order_items_order_date,
#             # purchase_order_package_model,
#             bundles,
#             categories,
#             catetory_tree,
#         ]

#         logger.info("Synchronous streams: %s", synchronous_streams[0].name)  # デバッグ

#         state_manager = ConnectorStateManager(state=self._state)

#         configured_streams = []

#         for stream in synchronous_streams:
        
#             logger.info(f"Stream {stream.name}: cursor_field={stream.cursor_field}, primary_key={stream.primary_key}")
#             legacy_state = state_manager.get_stream_state(stream.name, stream.namespace)
            
#             if stream.cursor_field:
#                 cursor_field = CursorField(stream.cursor_field)
#                 cursor = ConcurrentCursor(
#                     stream.name,
#                     stream.namespace,
#                     legacy_state,
#                     self.message_repository,
#                     state_manager,
#                     stream.state_converter,
#                     cursor_field,
#                     # self._get_slice_boundary_fields(stream, state_manager),
#                     stream.get_slice_boundary_fields(state_manager),
#                     pendulum.from_timestamp(_START_DATE, tz='UTC'),
#                     EpochValueConcurrentStreamStateConverter.get_end_provider()
#                 )
#             else:
#                 cursor = FinalStateCursor(stream._name, stream.namespace, self.message_repository)
#             configured_streams.append(
#                     StreamFacade.create_from_stream(stream,
#                                                 self,
#                                                 logger,
#                                                 legacy_state,
#                                                 cursor)
#                 )
#         logger.info("Configured streams: %s", [s.primary_key for s in configured_streams])
#         return configured_streams
    
#     def spec(self, logger: Logger) -> ConnectorSpecification:
#         spec = super().spec(logger)
#         return spec


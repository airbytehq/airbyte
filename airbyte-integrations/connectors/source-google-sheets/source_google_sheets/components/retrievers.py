#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import dpath
import requests
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.models.declarative_component_schema import HttpRequester
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.partition_routers.single_partition_router import SinglePartitionRouter
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.types import StreamSlice
from source_google_sheets.helpers_ import Helpers


class RangeRetriever(SimpleRetriever):
    parameters: Mapping[str, Any]

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     factory_constructor = ModelToComponentFactory(emit_connector_builder_messages=False)
    #     parameters = kwargs.get("parameters")
    #     self.stream_slicer: StreamSlicer = RangePartitionRouter(
    #         parameters={}, row_count=parameters.get("row_count", 0), batch_size=self.config.get("batch_size", 200)
    #     )
    #     sheet_headers_requester_definition = parameters.get("sheet_headers_requester")
    #     sheet_headers_requester_name = sheet_headers_requester_definition.get("$parameters", {}).get("name", "")
    #     self.sheet_headers_requester = factory_constructor.create_component(
    #         model_type=HttpRequester,
    #         component_definition=sheet_headers_requester_definition,
    #         config=self.config,
    #         name=sheet_headers_requester_name,
    #     )

    # def __post_init__(self, parameters: Mapping[str, Any]) -> None:
    #     super().__post_init__(parameters)
    #     factory_constructor = ModelToComponentFactory(emit_connector_builder_messages=False)
    #     # parameters = kwargs.get("parameters")
    #     self.stream_slicer: StreamSlicer = RangePartitionRouter(
    #         parameters={}, row_count=parameters.get("row_count", 0), batch_size=self.config.get("batch_size", 200)
    #     )
    #     sheet_headers_requester_definition = parameters.get("sheet_headers_requester")
    #     sheet_headers_requester_name = sheet_headers_requester_definition.get("$parameters", {}).get("name", "")
    #     self.sheet_headers_requester = factory_constructor.create_component(
    #         model_type=HttpRequester,
    #         component_definition=sheet_headers_requester_definition,
    #         config=self.config,
    #         name=sheet_headers_requester_name,
    #     )

    def stream_slices(self) -> Iterable[Optional[StreamSlice]]:  # type: ignore
        return self.stream_slicer.stream_slices()

    #
    # def get_sheet_headers(self):
    #     sheet_headers = self.sheet_headers_requester.send_request()
    #     return sheet_headers
    #
    # def read_records(
    #     self,
    #     records_schema: Mapping[str, Any],
    #     stream_slice: Optional[StreamSlice] = None,
    # ) -> Iterable[StreamData]:
    #     yield from super().read_records(records_schema=records_schema, stream_slice=stream_slice)
    #
    # def _parse_response(
    #     self,
    #     response: Optional[requests.Response],
    #     stream_state: StreamState,
    #     records_schema: Mapping[str, Any],
    #     stream_slice: Optional[StreamSlice] = None,
    #     next_page_token: Optional[Mapping[str, Any]] = None,
    # ) -> Iterable[Record]:
    #     if not response:
    #         self._last_response = None
    #         yield from []
    #     else:
    #         get_sheet_headers = self.get_sheet_headers()
    #         self._last_response = response
    #         # TODO: add something here or inside select records or record_slector
    #         # airbyte-integrations/connectors/source-google-sheets/.venv/lib/python3.10/site-packages/airbyte_cdk/sources/declarative/extractors/record_selector.py
    #         record_generator = self.record_selector.select_records(
    #             response=response,
    #             stream_state=stream_state,
    #             records_schema=records_schema,
    #             stream_slice=stream_slice,
    #             next_page_token=next_page_token,
    #         )
    #         self._last_page_size = 0
    #         for record in record_generator:
    #             self._last_page_size += 1
    #             self._last_record = record
    #             yield record

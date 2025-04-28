#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

import dpath
import requests
from airbyte_cdk.sources.declarative.partition_routers.list_partition_router import ListPartitionRouter
from airbyte_cdk import (
    BearerAuthenticator,
    CursorPaginationStrategy,
    DeclarativeStream,
    DefaultPaginator,
    DpathExtractor,
    HttpMethod,
    HttpRequester,
    JsonDecoder,
    MessageRepository,
    RecordSelector,
    RequestOption,
    RequestOptionType,
    SimpleRetriever,
    StreamSlice,
)

from airbyte_cdk.entrypoint import logger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.decoders import Decoder, JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
# from source_hubspot.streams import AssociationsStream


@dataclass
class NewtoLegacyFieldTransformation(RecordTransformation):
    """
    Implements a custom transformation which adds the legacy field equivalent of v2 fields for streams which contain Deals and Contacts entities.

    This custom implmentation was developed in lieu of the AddFields component due to the dynamic-nature of the record properties for the HubSpot source. Each

    For example:
    hs_v2_date_exited_{stage_id} -> hs_date_exited_{stage_id} where {stage_id} is a user-generated value
    """

    field_mapping: Mapping[str, str]

    def transform(
        self,
        record_or_schema: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        """
        Transform a record in place by adding fields directly to the record by manipulating the injected fields into a legacy field to avoid breaking syncs.

        :param record_or_schema: The input record or schema to be transformed.
        """
        is_record = record_or_schema.get("properties") is not None

        for field, value in list(record_or_schema.get("properties", record_or_schema).items()):
            for legacy_field, new_field in self.field_mapping.items():
                if new_field in field:
                    transformed_field = field.replace(new_field, legacy_field)

                    if legacy_field == "hs_lifecyclestage_" and not transformed_field.endswith("_date"):
                        transformed_field += "_date"

                    if is_record:
                        if record_or_schema["properties"].get(transformed_field) is None:
                            record_or_schema["properties"][transformed_field] = value
                    else:
                        if record_or_schema.get(transformed_field) is None:
                            record_or_schema[transformed_field] = value


@dataclass
class HubspotAssociationsExtractor(RecordExtractor):
    """
    Custom record extractor which parses the JSON response from Hubspot and for each instance returned for the specified
    object type (ex. Contacts, Deals, etc.), yields records for every requested property. Because this is a property
    history stream, an individual property can yield multiple records representing the previous version of that property.

    The custom behavior of this component is:
    - Iterating over and extracting property history instances as individual records
    - Injecting fields from out levels of the response into yielded records to be used as primary keys
    """

    field_path: List[Union[InterpolatedString, str]]
    entity_primary_key: str
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = field(default_factory=lambda: JsonDecoder(parameters={}))

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._field_path = [InterpolatedString.create(path, parameters=parameters) for path in self.field_path]
        for path_index in range(len(self.field_path)):
            if isinstance(self.field_path[path_index], str):
                self._field_path[path_index] = InterpolatedString.create(self.field_path[path_index], parameters=parameters)

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        for body in self.decoder.decode(response):
            if len(self._field_path) == 0:
                extracted = body
            else:
                path = [path.eval(self.config) for path in self._field_path]
                if "*" in path:
                    extracted = dpath.values(body, path)
                else:
                    extracted = dpath.get(body, path, default=[])  # type: ignore # extracted will be a MutableMapping, given input data structure
            if isinstance(extracted, list):
                records = extracted
            elif extracted:
                raise ValueError(f"field_path should always point towards a list field in the response body")

            yield from records


@dataclass
class HubspotCRMSearchPaginationStrategy(PaginationStrategy):
    """
    This pagination strategy will return latest record cursor for the next_page_token after hitting records count limit
    """

    page_size: int
    primary_key: str = "id"
    RECORDS_LIMIT = 20

    @property
    def initial_token(self) -> Optional[Any]:
        return {"after": 0}

    def next_page_token(
            self,
            response: requests.Response,
            last_page_size: int,
            last_record: Optional[Record],
            last_page_token_value: Optional[Any] = None,
    ) -> Optional[Any]:
        if last_page_token_value and last_page_token_value.get("after", 0) + last_page_size > self.RECORDS_LIMIT:
            return {"after": 0, "id": int(last_record[self.primary_key]) + 1}

        # Stop paginating when there are fewer records than the page size or the current page has no records
        if (last_page_size < self.page_size) or last_page_size == 0:
            return None

        return {"after": last_page_token_value["after"] + last_page_size}

    def get_page_size(self) -> Optional[int]:
        return self.page_size

#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

import dpath
import requests

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
from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.selective_authenticator import SelectiveAuthenticator
from airbyte_cdk.sources.declarative.auth.token_provider import InterpolatedStringTokenProvider
from airbyte_cdk.sources.declarative.decoders import Decoder, JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.partition_routers.list_partition_router import ListPartitionRouter
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


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


class MigrateEmptyStringState(StateMigration):
    cursor_field: str
    config: Config

    def __init__(self, cursor_field, config: Config):
        self.cursor_field = cursor_field
        self.config = config

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        # if start date wasn't provided in the config default date will be used
        start_date = self.config.get("start_date", "2006-06-01T00:00:00.000Z")
        return {self.cursor_field: start_date}

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return stream_state.get(self.cursor_field) == ""


class HubspotFlattenAssociationsTransformation(RecordTransformation):
    """
    A record transformation that flattens the `associations` field in HubSpot records.

    This transformation takes a nested dictionary under the `associations` key and extracts the IDs
    of associated objects. The extracted lists of IDs are added as new top-level fields in the record,
    using the association name as the key (spaces replaced with underscores).

    Example:
        Input:
        {
            "id": 1,
            "associations": {
                "Contacts": {"results": [{"id": 101}, {"id": 102}]}
            }
        }

        Output:
        {
            "id": 1,
            "Contacts": [101, 102]
        }
    """

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        if "associations" in record:
            associations = record.pop("associations")
            for name, association in associations.items():
                record[name.replace(" ", "_")] = [row["id"] for row in association.get("results", [])]


@dataclass
class HubspotAssociationsExtractor(RecordExtractor):
    """
    Custom extractor for HubSpot association-enriched records.

    This extractor:
    - Navigates a specified `field_path` within the JSON response to extract a list of primary entities.
    - Gets records IDs to use in associations retriever body.
    - Uses a secondary retriever to fetch associated objects for each entity (based on provided `associations_list`).
    - Merges associated object IDs back into each entity's record under the corresponding association name.

    Attributes:
        field_path: Path to the list of records in the API response.
        entity_primary_key: The field used for associations retriever endpoint.
        associations_list: List of associations to fetch (e.g., ["contacts", "companies"]).
    """

    field_path: List[Union[InterpolatedString, str]]
    entity_primary_key: str
    associations_list: List[str]
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

            records_by_pk = {record["id"]: record for record in records}
            identifiers = list(map(lambda x: x["id"], records))

            assoc_retriever = build_associations_retriever(
                associations_list=self.associations_list,
                ids=identifiers,
                parent_entity=self.entity_primary_key,
                config=self.config,
            )

            slices = assoc_retriever.stream_slices()

            for _slice in slices:
                logger.debug(f"Reading {_slice} associations of {self.entity_primary_key}")
                associations = assoc_retriever.read_records({}, stream_slice=_slice)
                for group in associations:
                    slice_value = _slice["association_name"]
                    current_record = records_by_pk[group["from"]["id"]]
                    associations_list = current_record.get(slice_value, [])
                    associations_list.extend(association["toObjectId"] for association in group["to"])
                    current_record[slice_value] = associations_list
            yield from records_by_pk.values()


def build_associations_retriever(
    *,
    associations_list: List[str],
    ids: List[str],
    parent_entity: str,
    config: Config,
) -> SimpleRetriever:
    """
    Returns a SimpleRetriever that hits
      POST /crm/v4/associations/{self.parent_stream.entity}/{stream_slice.association}/batch/read
    """

    parameters: Mapping[str, Any] = {}

    access_token = config["credentials"]["access_token"]
    bearer_authenticator = BearerAuthenticator(
        token_provider=InterpolatedStringTokenProvider(
            api_token=access_token,
            config=config,
            parameters=parameters,
        ),
        config=config,
        parameters=parameters,
    )

    # Use default values to create a component if another authentication method is used.
    # If values are missing it will fail in the parent stream
    oauth_authenticator = DeclarativeOauth2Authenticator(
        config=config,
        parameters=parameters,
        client_id=config["credentials"].get("client_id", "client_id"),
        client_secret=config["credentials"].get("client_secret", "client_secret"),
        refresh_token=config["credentials"].get("refresh_token", "refresh_token"),
        token_refresh_endpoint="https://api.hubapi.com/oauth/v1/token",
    )

    authenticator = SelectiveAuthenticator(
        config,
        authenticators={"Private App Credentials": bearer_authenticator, "OAuth Credentials": oauth_authenticator},
        authenticator_selection_path=["credentials", "credentials_title"],
    )
    # HTTP requester
    requester = HttpRequester(
        name="associations",
        url_base="https://api.hubapi.com",
        path=f"/crm/v4/associations/{parent_entity}/" + "{{ stream_slice['association_name'] }}/batch/read",
        http_method="POST",
        authenticator=authenticator,
        request_options_provider=InterpolatedRequestOptionsProvider(
            request_body_json={
                "inputs": [{"id": id} for id in ids],
            },
            config=config,
            parameters=parameters,
        ),
        config=config,
        parameters=parameters,
    )

    # Slice over IDs emitted by the parent stream
    slicer = ListPartitionRouter(values=associations_list, cursor_field="association_name", config=config, parameters=parameters)

    # Record selector
    selector = RecordSelector(
        extractor=DpathExtractor(field_path=["results"], config=config, parameters=parameters),
        schema_normalization=TypeTransformer(TransformConfig.NoTransform),
        record_filter=None,
        transformations=[],
        config=config,
        parameters=parameters,
    )

    # The retriever
    return SimpleRetriever(
        name="associations",
        requester=requester,
        record_selector=selector,
        paginator=None,  # batch/read never paginates
        stream_slicer=slicer,
        config=config,
        parameters=parameters,
    )


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

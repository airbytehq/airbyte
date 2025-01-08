#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests

from airbyte_cdk.sources.streams.http import HttpClient, HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_airtable.airtable_backoff_strategy import AirtableBackoffStrategy
from source_airtable.airtable_error_handler import AirtableErrorHandler
from source_airtable.schema_helpers import SchemaHelpers


URL_BASE: str = "https://api.airtable.com/v0/"


class AirtableBases(HttpStream):
    def __init__(self, **kwargs):
        authenticator = kwargs.get("authenticator")
        backoff_strategy = AirtableBackoffStrategy(self.logger)
        error_handler = AirtableErrorHandler(logger=self.logger, authenticator=authenticator)

        self._http_client = HttpClient(
            name=self.name,
            logger=self.logger,
            error_handler=error_handler,
            backoff_strategy=backoff_strategy,
            authenticator=authenticator,
        )

    url_base = URL_BASE
    primary_key = None
    name = "bases"

    def path(self, **kwargs) -> str:
        """
        Documentation: https://airtable.com/developers/web/api/list-bases
        """
        return "meta/bases"

    def next_page_token(self, response: requests.Response, **kwargs) -> Optional[Mapping[str, Any]]:
        """
        The bases list could be more than 100 records, therefore the pagination is required to fetch all of them.
        """
        next_page = response.json().get("offset")
        if next_page:
            return {"offset": next_page}
        return None

    def request_params(self, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> Mapping[str, Any]:
        params = {}
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Mapping[str, Any]:
        """
        Example output:
            {
                'bases': [
                    {'id': '_some_id_', 'name': 'users', 'permissionLevel': 'create'},
                    {'id': '_some_id_', 'name': 'Test Base', 'permissionLevel': 'create'},
                ]
            }
        """
        records = response.json().get(self.name)
        for base in records:
            if base.get("permissionLevel") == "none":
                if isinstance(self._http_client._session.auth, TokenAuthenticator):
                    additional_message = "if you'd like to see tables from this base, add base to the Access list for Personal Access Token, see Airtable docs for more info: https://support.airtable.com/docs/creating-and-using-api-keys-and-access-tokens#understanding-personal-access-token-basic-actions"
                else:
                    additional_message = "reauthenticate and add this base to the Access list, see Airtable docs for more info: https://support.airtable.com/docs/third-party-integrations-via-oauth-overview#granting-access-to-airtable-workspaces-bases"
                self.logger.warning(
                    f"Skipping base `{base.get('name')}` with id `{base.get('id')}`: Not enough permissions, {additional_message}"
                )
            else:
                yield base


class AirtableTables(AirtableBases):
    def __init__(self, base_id: list, **kwargs):
        super().__init__(**kwargs)
        self.base_id = base_id

    name = "tables"

    def path(self, **kwargs) -> str:
        """
        Documentation: https://airtable.com/developers/web/api/list-bases
        """
        return f"{super().path()}/{self.base_id}/tables"


class AirtableStream(HttpStream, ABC):
    def __init__(self, stream_path: str, stream_name: str, stream_schema, table_name: str, **kwargs):
        self.stream_name = stream_name
        self.stream_path = stream_path
        self.stream_schema = stream_schema
        self.table_name = table_name

        backoff_strategy = AirtableBackoffStrategy(self.logger)
        error_handler = HttpStatusErrorHandler(logger=self.logger)

        self._http_client = HttpClient(
            name=self.name,
            logger=self.logger,
            error_handler=error_handler,
            backoff_strategy=backoff_strategy,
            authenticator=kwargs.get("authenticator"),
        )

    url_base = URL_BASE
    primary_key = "id"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    @property
    def name(self):
        return self.stream_name

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.stream_schema

    def next_page_token(self, response: requests.Response, **kwargs) -> Optional[Mapping[str, Any]]:
        next_page = response.json().get("offset")
        if next_page:
            return {"offset": next_page}
        return None

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        """
        All available params: https://airtable.com/developers/web/api/list-records#query
        """
        params = {}
        if next_page_token:
            params.update(next_page_token)
        return params

    def process_records(self, records) -> Iterable[Mapping[str, Any]]:
        for record in records:
            data = record.get("fields")
            if len(data) > 0:
                yield {
                    "_airtable_id": record.get("id"),
                    "_airtable_created_time": record.get("createdTime"),
                    "_airtable_table_name": self.table_name,
                    **{SchemaHelpers.clean_name(k): v for k, v in data.items()},
                }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get("records", [])
        yield from self.process_records(records)

    def path(self, **kwargs) -> str:
        return self.stream_path

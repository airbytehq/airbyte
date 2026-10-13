# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections import Counter
from typing import Any, Iterator, List, Mapping, MutableMapping, Tuple, cast

import requests
from requests_oauthlib import OAuth1

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .errors import (
    DuplicateTableNameError,
    raise_for_netsuite_status,
)
from .streams import SuiteqlStream
from .validation import (
    SuiteQLCatalogStreamValidator,
    SuiteQLRealmValidator,
    SuiteQLSourceConfig,
    SuiteQLTableConfig,
    SuiteQLTableValidator,
)


class SourceNetsuiteSuiteql(AbstractSource):
    def base_url(self, config: SuiteQLSourceConfig) -> str:
        SuiteQLRealmValidator.validate(config["realm"])
        account_subdomain = config["realm"].replace("_", "-").lower()
        return f"https://{account_subdomain}.suitetalk.api.netsuite.com"

    def auth(self, config: SuiteQLSourceConfig) -> OAuth1:
        return OAuth1(
            client_key=config["consumer_key"],
            client_secret=config["consumer_secret"],
            resource_owner_key=config["token_key"],
            resource_owner_secret=config["token_secret"],
            realm=config["realm"].replace("-", "_").upper(),
            signature_method="HMAC-SHA256",
        )

    def validate_tables(self, config: SuiteQLSourceConfig) -> None:
        tables = config["tables"]
        names = [table["table_name"] for table in tables]
        duplicates = [name for name, count in Counter(names).items() if count > 1]
        if duplicates:
            raise DuplicateTableNameError(duplicates)

        for table in tables:
            SuiteQLTableValidator(table).validate()

    def streams(self, config: SuiteQLSourceConfig) -> List[Stream]:
        self.validate_tables(config)
        auth = self.auth(config)
        base_url = self.base_url(config)
        page_size = config.get("page_size", 1000)
        tables = config["tables"]

        return [self._get_stream(table=table, base_url=base_url, page_size=page_size, auth=auth) for table in tables]

    def discover(self, logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        catalog = super().discover(logger, config)
        for stream in catalog.streams:
            stream.source_defined_cursor = False
        return catalog

    def read(
        self,
        logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, Any] | None = None,
    ) -> Iterator[AirbyteMessage]:
        # spec validation runs before read, so casting is safe here for type checking
        source_config = cast(SuiteQLSourceConfig, config)
        configured_tables = self._configured_streams_by_name(catalog)
        tables = []

        for table in source_config["tables"]:
            configured_stream = configured_tables.get(table["table_name"])

            # prevent modifying the original table configuration
            configured_table = dict(table)

            if configured_stream:
                fields = SuiteQLCatalogStreamValidator(configured_stream).table_fields()
                configured_table.update(fields)
                SuiteQLTableValidator(configured_table).validate()

            tables.append(configured_table)

        return super().read(
            logger,
            {**source_config, "tables": tables},
            catalog,
            state,
        )

    def check_connection(self, logger, config: SuiteQLSourceConfig) -> Tuple[bool, Any]:
        try:
            self.validate_tables(config)
            session = self._get_session(self.auth(config))
            endpoint = self.base_url(config) + SuiteqlStream.api_path

            for table in config["tables"]:
                self._check_table(session, endpoint, table)

            return True, None

        except (KeyError, ValueError, requests.RequestException) as error:
            return False, error

    def _get_session(self, auth: OAuth1) -> requests.Session:
        session = requests.Session()
        session.auth = auth
        return session

    def _check_table(
        self,
        session: requests.Session,
        endpoint: str,
        table: SuiteQLTableConfig,
    ) -> None:
        response = session.post(
            endpoint,
            headers={"Prefer": "transient"},
            params={"limit": 1, "offset": 0},
            json={
                "q": SuiteqlStream.build_query(
                    table["table_name"],
                    table.get("primary_key", []),
                    table.get("cursor_field"),
                )
            },
        )
        raise_for_netsuite_status(response)

    def _get_stream(
        self,
        table: SuiteQLTableConfig,
        base_url: str,
        page_size: int,
        auth: OAuth1,
    ) -> SuiteqlStream:
        return SuiteqlStream(
            table_name=table["table_name"],
            base_url=base_url,
            page_size=page_size,
            auth=auth,
            primary_key=table.get("primary_key", []),
            cursor_field=table.get("cursor_field"),
        )

    def _configured_streams_by_name(
        self,
        catalog: ConfiguredAirbyteCatalog,
    ) -> dict[str, ConfiguredAirbyteStream]:
        configured_streams = {}
        for configured_stream in catalog.streams:
            configured_streams[configured_stream.stream.name] = configured_stream
        return configured_streams

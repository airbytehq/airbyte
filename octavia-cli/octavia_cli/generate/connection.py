#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_api_client import api
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody


class Connection:
    def __init__(self, api_client, source_id):
        self.api_client = api_client
        self.source_api = api.source_api.SourceApi(api_client)
        self.source_id = source_id

    def get_source_catalog(self):
        source_id_request_body = SourceIdRequestBody(source_id=self.source_id)
        catalog = self.source_api.discover_schema_for_source(source_id_request_body, _check_return_type=False).catalog
        return catalog

    def get_streams(self) -> dict:
        streams = self.get_source_catalog().get("streams")
        return streams

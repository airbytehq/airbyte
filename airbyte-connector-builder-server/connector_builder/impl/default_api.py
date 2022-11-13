#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from connector_builder.generated.apis.default_api_interface import DefaultApi
from connector_builder.generated.models.stream_read import StreamRead
from connector_builder.generated.models.stream_read_request_body import StreamReadRequestBody
from connector_builder.generated.models.streams_list_read import StreamsListRead
from connector_builder.generated.models.streams_list_request_body import StreamsListRequestBody
from fastapi import Body


class DefaultApiImpl(DefaultApi):
    async def get_manifest_template(self) -> str:
        return """version: "0.1.0"

        definitions:
          selector:
            extractor:
              field_pointer: []
          requester:
            url_base: "https://example.com"
            http_method: "GET"
            authenticator:
              type: BearerAuthenticator
              api_token: "{{ config['api_key'] }}"
          retriever:
            record_selector:
              $ref: "*ref(definitions.selector)"
            paginator:
              type: NoPagination
            requester:
              $ref: "*ref(definitions.requester)"
          base_stream:
            retriever:
              $ref: "*ref(definitions.retriever)"
          customers_stream:
            $ref: "*ref(definitions.base_stream)"
            $options:
              name: "customers"
              primary_key: "id"
              path: "/example"

        streams:
          - "*ref(definitions.customers_stream)"

        check:
          stream_names:
            - "customers"

        spec:
          documentation_url: https://docsurl.com
          connection_specification:
            title: Source Name Spec
            type: object
            required:
              - api_key
            additionalProperties: true
            properties:
              # 'TODO: This schema defines the configuration required for the source. This usually involves metadata such as database and/or authentication information.':
              api_key:
                type: string
                description: API Key
"""

    async def list_streams(self, streams_list_request_body: StreamsListRequestBody = Body(None, description="")) -> StreamsListRead:
        raise Exception("not yet implemented")

    async def read_stream(self, stream_read_request_body: StreamReadRequestBody = Body(None, description="")) -> StreamRead:
        raise Exception("not yet implemented")

#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.testing.scenario_builder import MockedHttpRequestsSourceBuilder, TestScenarioBuilder

_MANIFEST = {
    "version": "0.30.0",
    "type": "DeclarativeSource",
    "definitions": {
        "selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
        "requester": {
            "url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester", "path": "/v1/path"
        },
        "retriever": {
            "type": "SimpleRetriever",
            "record_selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
            "paginator": {"type": "NoPagination"},
            "requester": {
                "$ref": "#/definitions/requester"
            }
        },
        "breathing_techniques_stream": {
            "name": "breathing-techniques",
            "schema_loader": {
                "type": "InlineSchemaLoader",
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                    }
                }
            },
            "retriever": {
                "$ref": "#/definitions/retriever"
            },
        },
    },
    "streams": [
        "#/definitions/breathing_techniques_stream"
    ],
    "check": {"stream_names": ["hashiras"], "type": "CheckStream"},
    "spec": {
        "type": "Spec",
        "connection_specification": {

        }
    }
}

_source = ManifestDeclarativeSource(_MANIFEST)

declarative_scenario = (
    TestScenarioBuilder(lambda builder: MockedHttpRequestsSourceBuilder(builder, _source))
    .set_name("declarative")
    .set_config({
        "streams": [{"name": "breathing-techniques"}] #FIXME this shouldn't be needed
    })
    .set_expected_catalog({
        "streams": [
            {
                "name": "breathing-techniques",
                "supported_sync_modes": ["full_refresh"],
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer"
                        }
                    }
                }

            }
        ]

    }).set_expected_records([{}])
).build()

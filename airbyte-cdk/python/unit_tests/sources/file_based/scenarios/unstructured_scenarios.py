#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import base64

from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from unit_tests.sources.file_based.scenarios.file_based_source_builder import FileBasedSourceBuilder
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder

simple_markdown_scenario = (
    TestScenarioBuilder()
    .set_name("simple_markdown_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "unstructured"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.md": {
                    "contents": bytes(
                        "# Title 1\n\n## Title 2\n\n### Title 3\n\n#### Title 4\n\n##### Title 5\n\n###### Title 6\n\n", "UTF-8"
                    ),
                    "last_modified": "2023-06-05T03:54:07.000Z",
                },
                "b.md": {
                    "contents": bytes("Just some text", "UTF-8"),
                    "last_modified": "2023-06-05T03:54:07.000Z",
                },
            }
        )
        .set_file_type("unstructured")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "document_key": {
                                "type": ["null", "string"],
                            },
                            "content": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string",
                            },
                            "_ab_source_file_url": {
                                "type": "string",
                            },
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "document_key": "a.md",
                    "content": "# Title 1\n\n## Title 2\n\n### Title 3\n\n#### Title 4\n\n##### Title 5\n\n###### Title 6\n\n",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.md",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "document_key": "b.md",
                    "content": "Just some text",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b.md",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

unstructured_invalid_file_type_discover_scenario = (
    TestScenarioBuilder()
    .set_name("unstructured_invalid_file_type_discover_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "unstructured"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.txt": {
                    "contents": bytes("Just a humble text file", "UTF-8"),
                    "last_modified": "2023-06-05T03:54:07.000Z",
                },
            }
        )
        .set_file_type("unstructured")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "document_key": {
                                "type": ["null", "string"],
                            },
                            "content": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string",
                            },
                            "_ab_source_file_url": {
                                "type": "string",
                            },
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records([])
    .set_expected_discover_error(AirbyteTracedException, "Error inferring schema from files")
).build()

unstructured_invalid_file_type_read_scenario = (
    TestScenarioBuilder()
    .set_name("unstructured_invalid_file_type_read_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "unstructured"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.md": {
                    "contents": bytes("A harmless markdown file", "UTF-8"),
                    "last_modified": "2023-06-05T03:54:07.000Z",
                },
                "b.txt": {
                    "contents": bytes("An evil text file", "UTF-8"),
                    "last_modified": "2023-06-05T03:54:07.000Z",
                },
            }
        )
        .set_file_type("unstructured")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "document_key": {
                                "type": ["null", "string"],
                            },
                            "content": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string",
                            },
                            "_ab_source_file_url": {
                                "type": "string",
                            },
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "document_key": "a.md",
                    "content": "A harmless markdown file",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.md",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

simple_pdf_scenario = (
    TestScenarioBuilder()
    .set_name("simple_pdf_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "unstructured"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "sample.pdf": {
                    # minimal pdf file inlined as base 64
                    "contents": base64.b64decode("JVBERi0xLjEKJcKlwrHDqwoKMSAwIG9iagogIDw8IC9UeXBlIC9DYXRhbG9nCiAgICAgL1BhZ2VzIDIgMCBSCiAgPj4KZW5kb2JqCgoyIDAgb2JqCiAgPDwgL1R5cGUgL1BhZ2VzCiAgICAgL0tpZHMgWzMgMCBSXQogICAgIC9Db3VudCAxCiAgICAgL01lZGlhQm94IFswIDAgMzAwIDE0NF0KICA+PgplbmRvYmoKCjMgMCBvYmoKICA8PCAgL1R5cGUgL1BhZ2UKICAgICAgL1BhcmVudCAyIDAgUgogICAgICAvUmVzb3VyY2VzCiAgICAgICA8PCAvRm9udAogICAgICAgICAgIDw8IC9GMQogICAgICAgICAgICAgICA8PCAvVHlwZSAvRm9udAogICAgICAgICAgICAgICAgICAvU3VidHlwZSAvVHlwZTEKICAgICAgICAgICAgICAgICAgL0Jhc2VGb250IC9UaW1lcy1Sb21hbgogICAgICAgICAgICAgICA+PgogICAgICAgICAgID4+CiAgICAgICA+PgogICAgICAvQ29udGVudHMgNCAwIFIKICA+PgplbmRvYmoKCjQgMCBvYmoKICA8PCAvTGVuZ3RoIDU1ID4+CnN0cmVhbQogIEJUCiAgICAvRjEgMTggVGYKICAgIDAgMCBUZAogICAgKEhlbGxvIFdvcmxkKSBUagogIEVUCmVuZHN0cmVhbQplbmRvYmoKCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxOCAwMDAwMCBuIAowMDAwMDAwMDc3IDAwMDAwIG4gCjAwMDAwMDAxNzggMDAwMDAgbiAKMDAwMDAwMDQ1NyAwMDAwMCBuIAp0cmFpbGVyCiAgPDwgIC9Sb290IDEgMCBSCiAgICAgIC9TaXplIDUKICA+PgpzdGFydHhyZWYKNTY1CiUlRU9GCg=="),
                    "last_modified": "2023-06-05T03:54:07.000Z",
                },
            }
        )
        .set_file_type("unstructured")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "document_key": {
                                "type": ["null", "string"],
                            },
                            "content": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string",
                            },
                            "_ab_source_file_url": {
                                "type": "string",
                            },
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "document_key": "sample.pdf",
                    "content": "# Hello World",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "sample.pdf",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

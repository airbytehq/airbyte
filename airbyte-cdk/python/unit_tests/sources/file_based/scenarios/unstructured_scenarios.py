#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import base64

import nltk
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from unit_tests.sources.file_based.scenarios.file_based_source_builder import FileBasedSourceBuilder
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder

# import nltk data for pdf parser
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

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

simple_unstructured_scenario = (
    TestScenarioBuilder()
    .set_name("simple_unstructured_scenario")
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
                    "contents": base64.b64decode(
                        "JVBERi0xLjEKJcKlwrHDqwoKMSAwIG9iagogIDw8IC9UeXBlIC9DYXRhbG9nCiAgICAgL1BhZ2VzIDIgMCBSCiAgPj4KZW5kb2JqCgoyIDAgb2JqCiAgPDwgL1R5cGUgL1BhZ2VzCiAgICAgL0tpZHMgWzMgMCBSXQogICAgIC9Db3VudCAxCiAgICAgL01lZGlhQm94IFswIDAgMzAwIDE0NF0KICA+PgplbmRvYmoKCjMgMCBvYmoKICA8PCAgL1R5cGUgL1BhZ2UKICAgICAgL1BhcmVudCAyIDAgUgogICAgICAvUmVzb3VyY2VzCiAgICAgICA8PCAvRm9udAogICAgICAgICAgIDw8IC9GMQogICAgICAgICAgICAgICA8PCAvVHlwZSAvRm9udAogICAgICAgICAgICAgICAgICAvU3VidHlwZSAvVHlwZTEKICAgICAgICAgICAgICAgICAgL0Jhc2VGb250IC9UaW1lcy1Sb21hbgogICAgICAgICAgICAgICA+PgogICAgICAgICAgID4+CiAgICAgICA+PgogICAgICAvQ29udGVudHMgNCAwIFIKICA+PgplbmRvYmoKCjQgMCBvYmoKICA8PCAvTGVuZ3RoIDU1ID4+CnN0cmVhbQogIEJUCiAgICAvRjEgMTggVGYKICAgIDAgMCBUZAogICAgKEhlbGxvIFdvcmxkKSBUagogIEVUCmVuZHN0cmVhbQplbmRvYmoKCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxOCAwMDAwMCBuIAowMDAwMDAwMDc3IDAwMDAwIG4gCjAwMDAwMDAxNzggMDAwMDAgbiAKMDAwMDAwMDQ1NyAwMDAwMCBuIAp0cmFpbGVyCiAgPDwgIC9Sb290IDEgMCBSCiAgICAgIC9TaXplIDUKICA+PgpzdGFydHhyZWYKNTY1CiUlRU9GCg=="
                    ),
                    "last_modified": "2023-06-05T03:54:07.000Z",
                },
                "sample.docx": {
                    # minimal docx file inlined as base 64
                    "contents": base64.b64decode(
                        "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"
                    ),
                    "last_modified": "2023-06-06T03:54:07.000Z",
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
            {
                "data": {
                    "document_key": "sample.docx",
                    "content": "# Content",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "sample.docx",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

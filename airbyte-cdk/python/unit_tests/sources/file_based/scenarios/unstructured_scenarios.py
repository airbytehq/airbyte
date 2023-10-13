#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os

from airbyte_cdk.utils.traced_exception import AirbyteTracedException
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
    .set_files(
        {
            "a.md": {
                "contents": bytes("# Title 1\n\n## Title 2\n\n### Title 3\n\n#### Title 4\n\n##### Title 5\n\n###### Title 6\n\n", "UTF-8"),
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.md": {
                "contents": bytes("Just some text", "UTF-8"),
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("unstructured")
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
    .set_files(
        {
            "a.txt": {
                "contents": bytes("Just a humble text file", "UTF-8"),
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("unstructured")
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
    .set_files(
        {
            "sample.pdf": {
                "contents": bytearray(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "sample.pdf"), mode="rb").read()),
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("unstructured")
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
                    "content": """# A Simple PDF File

This is a small demonstration .pdf file -

just for use in the Virtual Mechanics tutorials. More text. And more text. And more text. And more text. And more text.

And more text. And more text. And more text. And more text. And more text. And more text. Boring, zzzzz. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text.

And more text. And more text. And more text. And more text. And more text. And more text. And more text. Even more. Continued on page 2 ...

# Simple PDF File 2

...continued from page 1. Yet more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. Oh, how boring typing this stuff. But not as boring as watching paint dry. And more text. And more text. And more text. And more text. Boring. More, a little more text. The end, and just as well.""",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "sample.pdf",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

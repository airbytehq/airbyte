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

json_schema = {
    "type": "object",
    "properties": {
        "content": {
            "type": ["null", "string"],
            "description": "Content of the file as markdown. Might be null if the file could not be parsed",
        },
        "document_key": {"type": ["null", "string"], "description": "Unique identifier of the document, e.g. the file path"},
        "_ab_source_file_parse_error": {
            "type": ["null", "string"],
            "description": "Error message if the file could not be parsed even though the file is supported",
        },
        "_ab_source_file_last_modified": {"type": "string"},
        "_ab_source_file_url": {"type": "string"},
    },
}

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
                "c": {
                    "contents": bytes("Detected via mime type", "UTF-8"),
                    "last_modified": "2023-06-05T03:54:07.000Z",
                    "mime_type": "text/markdown",
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
                    "json_schema": json_schema,
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "source_defined_primary_key": [["document_key"]],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
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
            {
                "data": {
                    "document_key": "c",
                    "content": "Detected via mime type",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "c",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

simple_txt_scenario = (
    TestScenarioBuilder()
    .set_name("simple_txt_scenario")
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
                    "contents": bytes("Just some raw text", "UTF-8"),
                    "last_modified": "2023-06-05T03:54:07.000Z",
                },
                "b": {
                    "contents": bytes("Detected via mime type", "UTF-8"),
                    "last_modified": "2023-06-05T03:54:07.000Z",
                    "mime_type": "text/plain",
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
                    "json_schema": json_schema,
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "source_defined_primary_key": [["document_key"]],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "document_key": "a.txt",
                    "content": "Just some raw text",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.txt",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "document_key": "b",
                    "content": "Detected via mime type",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

# If skip unprocessable file types is set to false, then discover will fail if it encounters a non-matching file type
unstructured_invalid_file_type_discover_scenario_no_skip = (
    TestScenarioBuilder()
    .set_name("unstructured_invalid_file_type_discover_scenario_no_skip")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "unstructured", "skip_unprocessable_files": False},
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
                "a.csv": {
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
                    "json_schema": json_schema,
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "source_defined_primary_key": [["document_key"]],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records([])
    .set_expected_discover_error(AirbyteTracedException, "Error inferring schema from files")
    .set_expected_read_error(
        AirbyteTracedException,
        "Please check the logged errors for more information.",
    )
).build()

# If skip unprocessable file types is set to true, then discover will succeed even if there are non-matching file types
unstructured_invalid_file_type_discover_scenario_skip = (
    TestScenarioBuilder()
    .set_name("unstructured_invalid_file_type_discover_scenario_skip")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "unstructured", "skip_unprocessable_files": True},
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
                "a.csv": {
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
                    "json_schema": json_schema,
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "source_defined_primary_key": [["document_key"]],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "document_key": "a.csv",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                    "_ab_source_file_parse_error": "Error parsing record. This could be due to a mismatch between the config's file type and the actual file type, or because the file or record is not parseable. Contact Support if you need assistance.\nfilename=a.csv message=File type FileType.CSV is not supported. Supported file types are FileType.MD, FileType.PDF, FileType.DOCX, FileType.PPTX, FileType.TXT",
                },
                "stream": "stream1",
            }
        ]
    )
).build()

# TODO When working on https://github.com/airbytehq/airbyte/issues/31605, this test should be split into two tests:
# 1. Test that the file is skipped if skip_unprocessable_files is set to true
# 2. Test that the sync fails if skip_unprocessable_files is set to false
unstructured_invalid_file_type_read_scenario = (
    TestScenarioBuilder()
    .set_name("unstructured_invalid_file_type_read_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "unstructured", "skip_unprocessable_files": False},
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
                "b.csv": {
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
                    "json_schema": json_schema,
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "source_defined_primary_key": [["document_key"]],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
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

pdf_file = base64.b64decode(
    "JVBERi0xLjEKJcKlwrHDqwoKMSAwIG9iagogIDw8IC9UeXBlIC9DYXRhbG9nCiAgICAgL1BhZ2VzIDIgMCBSCiAgPj4KZW5kb2JqCgoyIDAgb2JqCiAgPDwgL1R5cGUgL1BhZ2VzCiAgICAgL0tpZHMgWzMgMCBSXQogICAgIC9Db3VudCAxCiAgICAgL01lZGlhQm94IFswIDAgMzAwIDE0NF0KICA+PgplbmRvYmoKCjMgMCBvYmoKICA8PCAgL1R5cGUgL1BhZ2UKICAgICAgL1BhcmVudCAyIDAgUgogICAgICAvUmVzb3VyY2VzCiAgICAgICA8PCAvRm9udAogICAgICAgICAgIDw8IC9GMQogICAgICAgICAgICAgICA8PCAvVHlwZSAvRm9udAogICAgICAgICAgICAgICAgICAvU3VidHlwZSAvVHlwZTEKICAgICAgICAgICAgICAgICAgL0Jhc2VGb250IC9UaW1lcy1Sb21hbgogICAgICAgICAgICAgICA+PgogICAgICAgICAgID4+CiAgICAgICA+PgogICAgICAvQ29udGVudHMgNCAwIFIKICA+PgplbmRvYmoKCjQgMCBvYmoKICA8PCAvTGVuZ3RoIDU1ID4+CnN0cmVhbQogIEJUCiAgICAvRjEgMTggVGYKICAgIDAgMCBUZAogICAgKEhlbGxvIFdvcmxkKSBUagogIEVUCmVuZHN0cmVhbQplbmRvYmoKCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxOCAwMDAwMCBuIAowMDAwMDAwMDc3IDAwMDAwIG4gCjAwMDAwMDAxNzggMDAwMDAgbiAKMDAwMDAwMDQ1NyAwMDAwMCBuIAp0cmFpbGVyCiAgPDwgIC9Sb290IDEgMCBSCiAgICAgIC9TaXplIDUKICA+PgpzdGFydHhyZWYKNTY1CiUlRU9GCg=="
)

docx_file = base64.b64decode(
    "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"
)

pptx_file = base64.b64decode(
    "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"
)

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
                    "contents": pdf_file,
                    "last_modified": "2023-06-05T03:54:07.000Z",
                },
                "sample.docx": {
                    # minimal docx file inlined as base 64
                    "contents": docx_file,
                    "last_modified": "2023-06-06T03:54:07.000Z",
                },
                "sample.pptx": {
                    # minimal pptx file inlined as base 64
                    "contents": pptx_file,
                    "last_modified": "2023-06-07T03:54:07.000Z",
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
                    "json_schema": json_schema,
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "source_defined_primary_key": [["document_key"]],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
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
            {
                "data": {
                    "document_key": "sample.pptx",
                    "content": "# Title",
                    "_ab_source_file_last_modified": "2023-06-07T03:54:07.000000Z",
                    "_ab_source_file_url": "sample.pptx",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

corrupted_file_scenario = (
    TestScenarioBuilder()
    .set_name("corrupted_file_scenario")
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
                    # bytes that can't be parsed as pdf
                    "contents": bytes("___ corrupted file ___", "utf-8"),
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
                    "json_schema": json_schema,
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "source_defined_primary_key": [["document_key"]],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "document_key": "sample.pdf",
                    "_ab_source_file_parse_error": "Error parsing record. This could be due to a mismatch between the config's file type and the actual file type, or because the file or record is not parseable. Contact Support if you need assistance.\nfilename=sample.pdf message=No /Root object! - Is this really a PDF?",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "sample.pdf",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

no_file_extension_unstructured_scenario = (
    TestScenarioBuilder()
    .set_name("no_file_extension_unstructured_scenario")
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
                "pdf_without_extension": {
                    # same file, but can't be detected via file extension
                    "contents": pdf_file,
                    "last_modified": "2023-06-05T03:54:07.000Z",
                },
                "docx_without_extension": {
                    # same file, but can't be detected via file extesion
                    "contents": docx_file,
                    "last_modified": "2023-06-06T03:54:07.000Z",
                },
                "pptx_without_extension": {
                    # minimal pptx file inlined as base 64
                    "contents": pptx_file,
                    "last_modified": "2023-06-07T03:54:07.000Z",
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
                    "json_schema": json_schema,
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "source_defined_primary_key": [["document_key"]],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "document_key": "pdf_without_extension",
                    "content": "# Hello World",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "pdf_without_extension",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "document_key": "docx_without_extension",
                    "content": "# Content",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "docx_without_extension",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "document_key": "pptx_without_extension",
                    "content": "# Title",
                    "_ab_source_file_last_modified": "2023-06-07T03:54:07.000000Z",
                    "_ab_source_file_url": "pptx_without_extension",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

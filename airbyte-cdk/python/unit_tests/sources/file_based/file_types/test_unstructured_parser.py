#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock, call, mock_open, patch

import pytest
import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.config.unstructured_format import APIParameterConfigModel, APIProcessingConfigModel, UnstructuredFormat
from airbyte_cdk.sources.file_based.exceptions import RecordParseError
from airbyte_cdk.sources.file_based.file_types import UnstructuredParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from unstructured.documents.elements import ElementMetadata, Formula, ListItem, Text, Title
from unstructured.file_utils.filetype import FileType

FILE_URI = "path/to/file.xyz"


@pytest.mark.parametrize(
    "filetype, format_config, raises",
    [
        pytest.param(
            FileType.MD,
            UnstructuredFormat(skip_unprocessable_files=False),
            False,
            id="markdown_file",
        ),
        pytest.param(
            FileType.CSV,
            UnstructuredFormat(skip_unprocessable_files=False),
            True,
            id="wrong_file_format",
        ),
        pytest.param(
            FileType.CSV,
            UnstructuredFormat(skip_unprocessable_files=True),
            False,
            id="wrong_file_format_skipping",
        ),
        pytest.param(
            FileType.PDF,
            UnstructuredFormat(skip_unprocessable_files=False),
            False,
            id="pdf_file",
        ),
        pytest.param(
            FileType.DOCX,
            UnstructuredFormat(skip_unprocessable_files=False),
            False,
            id="docx_file",
        ),
        pytest.param(
            FileType.PPTX,
            UnstructuredFormat(skip_unprocessable_files=False),
            False,
            id="pptx_file",
        ),
    ],
)
@patch("airbyte_cdk.sources.file_based.file_types.unstructured_parser.detect_filetype")
def test_infer_schema(mock_detect_filetype, filetype, format_config, raises):
    # use a fresh event loop to avoid leaking into other tests
    main_loop = asyncio.get_event_loop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    stream_reader = MagicMock()
    mock_open(stream_reader.open_file)
    fake_file = MagicMock()
    fake_file.uri = FILE_URI
    logger = MagicMock()
    mock_detect_filetype.return_value = filetype
    config = MagicMock()
    config.format = format_config
    if raises:
        with pytest.raises(RecordParseError):
            loop.run_until_complete(UnstructuredParser().infer_schema(config, fake_file, stream_reader, logger))
    else:
        schema = loop.run_until_complete(UnstructuredParser().infer_schema(config, MagicMock(), MagicMock(), MagicMock()))
        assert schema == {
            "content": {"type": "string", "description": "Content of the file as markdown. Might be null if the file could not be parsed"},
            "document_key": {"type": "string", "description": "Unique identifier of the document, e.g. the file path"},
            "_ab_source_file_parse_error": {
                "type": "string",
                "description": "Error message if the file could not be parsed even though the file is supported",
            },
        }
    loop.close()
    asyncio.set_event_loop(main_loop)


@pytest.mark.parametrize(
    "filetype, format_config, parse_result, raises, expected_records, parsing_error",
    [
        pytest.param(
            FileType.MD,
            UnstructuredFormat(skip_unprocessable_files=False),
            "test",
            False,
            [
                {
                    "content": "test",
                    "document_key": FILE_URI,
                    "_ab_source_file_parse_error": None,
                }
            ],
            False,
            id="markdown_file",
        ),
        pytest.param(
            FileType.CSV,
            UnstructuredFormat(skip_unprocessable_files=False),
            None,
            True,
            None,
            False,
            id="wrong_file_format",
        ),
        pytest.param(
            FileType.CSV,
            UnstructuredFormat(skip_unprocessable_files=True),
            None,
            False,
            [
                {
                    "content": None,
                    "document_key": FILE_URI,
                    "_ab_source_file_parse_error": "Error parsing record. This could be due to a mismatch between the config's file type and the actual file type, or because the file or record is not parseable. Contact Support if you need assistance.\nfilename=path/to/file.xyz message=File type FileType.CSV is not supported. Supported file types are FileType.MD, FileType.PDF, FileType.DOCX, FileType.PPTX, FileType.TXT",
                }
            ],
            False,
            id="skip_unprocessable_files",
        ),
        pytest.param(
            FileType.PDF,
            UnstructuredFormat(skip_unprocessable_files=False),
            [
                Title("heading"),
                Text("This is the text"),
                ListItem("This is a list item"),
                Formula("This is a formula"),
            ],
            False,
            [
                {
                    "content": "# heading\n\nThis is the text\n\n- This is a list item\n\n```\nThis is a formula\n```",
                    "document_key": FILE_URI,
                    "_ab_source_file_parse_error": None,
                }
            ],
            False,
            id="pdf_file",
        ),
        pytest.param(
            FileType.PDF,
            UnstructuredFormat(skip_unprocessable_files=False),
            [
                Title("first level heading", metadata=ElementMetadata(category_depth=1)),
                Title("second level heading", metadata=ElementMetadata(category_depth=2)),
            ],
            False,
            [
                {
                    "content": "# first level heading\n\n## second level heading",
                    "document_key": FILE_URI,
                    "_ab_source_file_parse_error": None,
                }
            ],
            False,
            id="multi_level_headings",
        ),
        pytest.param(
            FileType.DOCX,
            UnstructuredFormat(skip_unprocessable_files=False),
            [
                Title("heading"),
                Text("This is the text"),
                ListItem("This is a list item"),
                Formula("This is a formula"),
            ],
            False,
            [
                {
                    "content": "# heading\n\nThis is the text\n\n- This is a list item\n\n```\nThis is a formula\n```",
                    "document_key": FILE_URI,
                    "_ab_source_file_parse_error": None,
                }
            ],
            False,
            id="docx_file",
        ),
        pytest.param(
            FileType.DOCX,
            UnstructuredFormat(skip_unprocessable_files=True),
            "",
            False,
            [
                {
                    "content": None,
                    "document_key": FILE_URI,
                    "_ab_source_file_parse_error": "Error parsing record. This could be due to a mismatch between the config's file type and the actual file type, or because the file or record is not parseable. Contact Support if you need assistance.\nfilename=path/to/file.xyz message=weird parsing error",
                }
            ],
            True,
            id="exception_during_parsing",
        ),
    ],
)
@patch("unstructured.partition.pdf.partition_pdf")
@patch("unstructured.partition.pptx.partition_pptx")
@patch("unstructured.partition.docx.partition_docx")
@patch("airbyte_cdk.sources.file_based.file_types.unstructured_parser.detect_filetype")
def test_parse_records(
    mock_detect_filetype,
    mock_partition_docx,
    mock_partition_pptx,
    mock_partition_pdf,
    filetype,
    format_config,
    parse_result,
    raises,
    expected_records,
    parsing_error,
):
    stream_reader = MagicMock()
    mock_open(stream_reader.open_file, read_data=bytes(str(parse_result), "utf-8"))
    fake_file = RemoteFile(uri=FILE_URI, last_modified=datetime.now())
    fake_file.uri = FILE_URI
    logger = MagicMock()
    config = MagicMock()
    config.format = format_config
    mock_detect_filetype.return_value = filetype
    if parsing_error:
        mock_partition_docx.side_effect = Exception("weird parsing error")
        mock_partition_pptx.side_effect = Exception("weird parsing error")
        mock_partition_pdf.side_effect = Exception("weird parsing error")
    else:
        mock_partition_docx.return_value = parse_result
        mock_partition_pptx.return_value = parse_result
        mock_partition_pdf.return_value = parse_result
    if raises:
        with pytest.raises(RecordParseError):
            list(UnstructuredParser().parse_records(config, fake_file, stream_reader, logger, MagicMock()))
    else:
        assert list(UnstructuredParser().parse_records(config, fake_file, stream_reader, logger, MagicMock())) == expected_records


@pytest.mark.parametrize(
    "format_config, raises_for_status, json_response, is_ok, expected_error",
    [
        pytest.param(
            UnstructuredFormat(skip_unprocessable_file_types=False),
            False,
            {"status": "ok"},
            True,
            None,
            id="local",
        ),
        pytest.param(
            UnstructuredFormat(skip_unprocessable_file_types=False, strategy="fast"),
            False,
            {"status": "ok"},
            True,
            None,
            id="local_ok_strategy",
        ),
        pytest.param(
            UnstructuredFormat(skip_unprocessable_file_types=False, strategy="hi_res"),
            False,
            {"status": "ok"},
            False,
            "Hi-res strategy is not supported for local processing",
            id="local_unsupported_strategy",
        ),
        pytest.param(
            UnstructuredFormat(skip_unprocessable_file_types=False, processing=APIProcessingConfigModel(mode="api", api_key="test")),
            False,
            [{"type": "Title", "text": "Airbyte source connection test"}],
            True,
            None,
            id="api_ok",
        ),
        pytest.param(
            UnstructuredFormat(skip_unprocessable_file_types=False, processing=APIProcessingConfigModel(mode="api", api_key="test")),
            True,
            None,
            False,
            "API error",
            id="api_error",
        ),
        pytest.param(
            UnstructuredFormat(skip_unprocessable_file_types=False, processing=APIProcessingConfigModel(mode="api", api_key="test")),
            False,
            {"unexpected": "response"},
            False,
            "Error",
            id="unexpected_handling_error",
        ),
    ],
)
@patch("airbyte_cdk.sources.file_based.file_types.unstructured_parser.requests")
def test_check_config(requests_mock, format_config, raises_for_status, json_response, is_ok, expected_error):
    mock_response = MagicMock()
    mock_response.json.return_value = json_response
    if raises_for_status:
        mock_response.raise_for_status.side_effect = Exception("API error")
    requests_mock.post.return_value = mock_response
    result, error = UnstructuredParser().check_config(FileBasedStreamConfig(name="test", format=format_config))
    assert result == is_ok
    if expected_error:
        assert expected_error in error


@pytest.mark.parametrize(
    "filetype, format_config, raises_for_status, file_content, json_response, expected_requests, raises, expected_records, http_status_code",
    [
        pytest.param(
            FileType.PDF,
            UnstructuredFormat(skip_unprocessable_file_types=False, processing=APIProcessingConfigModel(mode="api", api_key="test")),
            None,
            "test",
            [{"type": "Text", "text": "test"}],
            [
                call(
                    "https://api.unstructured.io/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "auto"},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                )
            ],
            False,
            [{"content": "test", "document_key": FILE_URI, "_ab_source_file_parse_error": None}],
            200,
            id="basic_request",
        ),
        pytest.param(
            FileType.PDF,
            UnstructuredFormat(
                skip_unprocessable_file_types=False,
                strategy="hi_res",
                processing=APIProcessingConfigModel(
                    mode="api",
                    api_key="test",
                    api_url="http://localhost:8000",
                    parameters=[
                        APIParameterConfigModel(name="include_page_breaks", value="true"),
                        APIParameterConfigModel(name="ocr_languages", value="eng"),
                        APIParameterConfigModel(name="ocr_languages", value="kor"),
                    ],
                ),
            ),
            None,
            "test",
            [{"type": "Text", "text": "test"}],
            [
                call(
                    "http://localhost:8000/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "hi_res", "include_page_breaks": "true", "ocr_languages": ["eng", "kor"]},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                )
            ],
            False,
            [{"content": "test", "document_key": FILE_URI, "_ab_source_file_parse_error": None}],
            200,
            id="request_with_params",
        ),
        pytest.param(
            FileType.MD,
            UnstructuredFormat(skip_unprocessable_file_types=False, processing=APIProcessingConfigModel(mode="api", api_key="test")),
            None,
            "# Mymarkdown",
            None,
            None,
            False,
            [{"content": "# Mymarkdown", "document_key": FILE_URI, "_ab_source_file_parse_error": None}],
            200,
            id="handle_markdown_locally",
        ),
        pytest.param(
            FileType.PDF,
            UnstructuredFormat(skip_unprocessable_file_types=False, processing=APIProcessingConfigModel(mode="api", api_key="test")),
            [
                requests.exceptions.RequestException("API error"),
                requests.exceptions.RequestException("API error"),
                requests.exceptions.RequestException("API error"),
                requests.exceptions.RequestException("API error"),
                requests.exceptions.RequestException("API error"),
            ],
            "test",
            None,
            [
                call(
                    "https://api.unstructured.io/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "auto"},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                ),
                call().raise_for_status(),
                call(
                    "https://api.unstructured.io/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "auto"},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                ),
                call().raise_for_status(),
                call(
                    "https://api.unstructured.io/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "auto"},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                ),
                call().raise_for_status(),
                call(
                    "https://api.unstructured.io/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "auto"},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                ),
                call().raise_for_status(),
                call(
                    "https://api.unstructured.io/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "auto"},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                ),
                call().raise_for_status(),
            ],
            True,
            None,
            200,
            id="retry_and_raise_on_api_error",
        ),
        pytest.param(
            FileType.PDF,
            UnstructuredFormat(skip_unprocessable_file_types=False, processing=APIProcessingConfigModel(mode="api", api_key="test")),
            [
                requests.exceptions.RequestException("API error"),
                requests.exceptions.RequestException("API error"),
                None,
            ],
            "test",
            [{"type": "Text", "text": "test"}],
            [
                call(
                    "https://api.unstructured.io/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "auto"},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                ),
                call().raise_for_status(),
                call(
                    "https://api.unstructured.io/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "auto"},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                ),
                call().raise_for_status(),
                call(
                    "https://api.unstructured.io/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "auto"},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                ),
                call().raise_for_status(),
            ],
            False,
            [{"content": "test", "document_key": FILE_URI, "_ab_source_file_parse_error": None}],
            200,
            id="retry_and_recover",
        ),
        pytest.param(
            FileType.PDF,
            UnstructuredFormat(skip_unprocessable_file_types=False, processing=APIProcessingConfigModel(mode="api", api_key="test")),
            [
                Exception("Unexpected error"),
            ],
            "test",
            [{"type": "Text", "text": "test"}],
            [
                call(
                    "https://api.unstructured.io/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "auto"},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                ),
                call().raise_for_status(),
            ],
            True,
            None,
            200,
            id="no_retry_on_unexpected_error",
        ),
        pytest.param(
            FileType.PDF,
            UnstructuredFormat(skip_unprocessable_file_types=False, processing=APIProcessingConfigModel(mode="api", api_key="test")),
            [
                requests.exceptions.RequestException("API error", response=MagicMock(status_code=400)),
            ],
            "test",
            [{"type": "Text", "text": "test"}],
            [
                call(
                    "https://api.unstructured.io/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "auto"},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                ),
                call().raise_for_status(),
            ],
            True,
            None,
            400,
            id="no_retry_on_400_error",
        ),
        pytest.param(
            FileType.PDF,
            UnstructuredFormat(skip_unprocessable_file_types=False, processing=APIProcessingConfigModel(mode="api", api_key="test")),
            None,
            "test",
            [{"detail": "Something went wrong"}],
            [
                call(
                    "https://api.unstructured.io/general/v0/general",
                    headers={"accept": "application/json", "unstructured-api-key": "test"},
                    data={"strategy": "auto"},
                    files={"files": ("filename", mock.ANY, "application/pdf")},
                ),
            ],
            False,
            [
                {
                    "content": None,
                    "document_key": FILE_URI,
                    "_ab_source_file_parse_error": "Error parsing record. This could be due to a mismatch between the config's file type and the actual file type, or because the file or record is not parseable. Contact Support if you need assistance.\nfilename=path/to/file.xyz message=[{'detail': 'Something went wrong'}]",
                }
            ],
            422,
            id="error_record_on_422_error",
        ),
    ],
)
@patch("airbyte_cdk.sources.file_based.file_types.unstructured_parser.requests")
@patch("airbyte_cdk.sources.file_based.file_types.unstructured_parser.detect_filetype")
@patch("time.sleep", side_effect=lambda _: None)
def test_parse_records_remotely(
    time_mock,
    mock_detect_filetype,
    requests_mock,
    filetype,
    format_config,
    raises_for_status,
    file_content,
    json_response,
    expected_requests,
    raises,
    expected_records,
    http_status_code,
):
    stream_reader = MagicMock()
    mock_open(stream_reader.open_file, read_data=bytes(str(file_content), "utf-8"))
    fake_file = RemoteFile(uri=FILE_URI, last_modified=datetime.now())
    fake_file.uri = FILE_URI
    logger = MagicMock()
    config = MagicMock()
    config.format = format_config
    mock_detect_filetype.return_value = filetype
    mock_response = MagicMock()
    mock_response.json.return_value = json_response
    mock_response.status_code = http_status_code
    if raises_for_status:
        mock_response.raise_for_status.side_effect = raises_for_status
    requests_mock.post.return_value = mock_response
    requests_mock.exceptions.RequestException = requests.exceptions.RequestException

    if raises:
        with pytest.raises(AirbyteTracedException) as exc:
            list(UnstructuredParser().parse_records(config, fake_file, stream_reader, logger, MagicMock()))
        # Failures from the API are treated as config errors
        assert exc.value.failure_type == FailureType.config_error
    else:
        assert list(UnstructuredParser().parse_records(config, fake_file, stream_reader, logger, MagicMock())) == expected_records

    if expected_requests:
        requests_mock.post.assert_has_calls(expected_requests)
    else:
        requests_mock.post.assert_not_called()

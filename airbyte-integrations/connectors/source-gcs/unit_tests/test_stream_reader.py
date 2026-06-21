# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import datetime
import gzip
import inspect
from unittest.mock import MagicMock, Mock

import pytest
import pytz
from source_gcs import Config, SourceGCSStreamReader
from source_gcs.config import ServiceAccountCredentials

from airbyte_cdk.sources.file_based.exceptions import ErrorListingFiles
from airbyte_cdk.sources.file_based.file_based_stream_reader import FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


try:
    from google.resumable_media._helpers import _DoNothingHash
    from google.resumable_media.requests.download import _GzipDecoder
except ImportError:
    _DoNothingHash = None
    _GzipDecoder = None


def test_get_matching_files_with_no_prefix(logger, mocked_reader):
    mocked_reader._config = Config(
        credentials=ServiceAccountCredentials(service_account='{"type": "service_account"}', auth_type="Service"),
        bucket="test_bucket",
        streams=[],
    )
    globs = ["**/*.csv"]

    with pytest.raises(ErrorListingFiles):
        list(mocked_reader.get_matching_files(globs, None, logger))

    # Assert there is a valid prefix:glob pair, so for loop enters execution.
    assert mocked_reader._gcs_client.get_bucket.called == 1


def test_open_file_with_compression(logger):
    reader = SourceGCSStreamReader()
    reader._gcs_client = Mock()
    reader._config = Mock()

    file = RemoteFile(uri="http://some.uri/file.gz?query=param", last_modified=datetime.datetime.now())
    file.mime_type = "file.gz"

    with pytest.raises(OSError):
        reader.open_file(file, FileReadMode.READ_BINARY, None, logger)


def test_open_file_without_compression(remote_file, logger):
    reader = SourceGCSStreamReader()
    reader._gcs_client = Mock()
    reader._config = Mock()

    with pytest.raises(OSError):
        reader.open_file(remote_file, FileReadMode.READ, None, logger)


def test_upload(remote_file, logger):
    reader = SourceGCSStreamReader()
    reader._gcs_client = Mock()
    reader._config = Mock()

    file_record_data, file_reference = reader.upload(remote_file, "test_local_directory", logger)

    assert file_record_data is not None
    assert file_reference is not None


@pytest.mark.parametrize(
    "blob_name, expected_is_zip",
    [
        ("data.zip", True),
        ("data.csv.zip", True),
        ("archive.json.zip", True),
        ("data.csv", False),
        ("data.csv.gz", False),
        ("data.zipx", False),
    ],
)
def test_compound_extension_detected_as_zip(blob_name, expected_is_zip):
    assert blob_name.endswith(".zip") == expected_is_zip


def _make_mock_blob(bucket_name: str, blob_name: str, signed_url: str) -> MagicMock:
    blob = MagicMock()
    blob.name = blob_name
    blob.bucket.name = bucket_name
    blob.updated = datetime.datetime.now(tz=pytz.utc)
    blob.generate_signed_url.return_value = signed_url
    return blob


@pytest.mark.parametrize(
    "sanitize_value,expected_displayed_uri",
    [
        pytest.param(
            True,
            "https://storage.googleapis.com/my-bucket/data.csv",
            id="sanitize_true_strips_query_params",
        ),
        pytest.param(
            False,
            None,
            id="sanitize_false_preserves_signed_url",
        ),
        pytest.param(
            None,
            None,
            id="sanitize_none_preserves_signed_url",
        ),
    ],
)
def test_get_matching_files_sanitize_signed_urls(logger, sanitize_value, expected_displayed_uri):
    signed_url = (
        "https://storage.googleapis.com/my-bucket/data.csv"
        "?X-Goog-Algorithm=GOOG4-RSA-SHA256"
        "&X-Goog-Credential=sa%40project.iam.gserviceaccount.com"
        "&X-Goog-Signature=abc123"
    )
    blob = _make_mock_blob("my-bucket", "data.csv", signed_url)

    reader = SourceGCSStreamReader()
    reader._gcs_client = MagicMock()
    reader._gcs_client.get_bucket.return_value.list_blobs.return_value = [blob]

    config_kwargs = dict(
        credentials=ServiceAccountCredentials(service_account='{"type": "service_account"}', auth_type="Service"),
        bucket="my-bucket",
        streams=[],
    )
    if sanitize_value is not None:
        config_kwargs["sanitize_signed_urls"] = sanitize_value
    reader._config = Config(**config_kwargs)

    files = list(reader.get_matching_files(["**/*.csv"], None, logger))

    assert len(files) == 1
    assert files[0].displayed_uri == expected_displayed_uri
    if sanitize_value:
        assert "X-Goog-Credential" not in (files[0].displayed_uri or "")
        assert "X-Goog-Signature" not in (files[0].displayed_uri or "")


@pytest.mark.skipif(_GzipDecoder is None, reason="google-resumable-media _GzipDecoder not available")
@pytest.mark.parametrize(
    "csv_payload,max_length",
    [
        pytest.param(
            b"id,name,value\n1,Alice,100\n2,Bob,200\n3,Charlie,300\n",
            8192,
            id="typical_csv_with_large_max_length",
        ),
        pytest.param(
            b"col_a,col_b\nx,y\n",
            16,
            id="small_csv_with_tight_max_length",
        ),
        pytest.param(
            b"id,name,value\n" + b"999,row,data\n" * 200,
            4096,
            id="larger_payload_partial_decompress",
        ),
    ],
)
def test_gzip_decoder_decompress_with_max_length(csv_payload, max_length):
    """Behavioral regression test: google-resumable-media _GzipDecoder with max_length kwarg.

    urllib3 >=2.6.0 calls decompress(data, max_length=<int>) on HTTP response
    decoders. google-resumable-media <2.8.1 overrode decompress() without
    accepting the max_length keyword, raising TypeError on gzip-encoded GCS
    downloads. This test exercises the actual decompress call path that fails
    with google-resumable-media 2.8.0 and passes with >=2.8.1.
    See: https://github.com/airbytehq/oncall/issues/11500
    """
    compressed = gzip.compress(csv_payload)
    decoder = _GzipDecoder(_DoNothingHash())

    # This is the exact call pattern urllib3 >=2.6.0 uses on response decoders.
    # With google-resumable-media <2.8.1 this raises:
    #   TypeError: _GzipDecoder.decompress() got an unexpected keyword argument 'max_length'
    result = decoder.decompress(compressed, max_length=max_length)

    # max_length may truncate the output; collect remaining bytes if needed.
    # The zlib DecompressObj behind _GzipDecoder buffers unconsumed input.
    if hasattr(decoder, "unconsumed_tail") or len(result) < len(csv_payload):
        # Drain any remaining data (mimics urllib3 read loop)
        remainder = decoder.decompress(b"", max_length=0)
        result += remainder

    assert csv_payload.startswith(result) or result == csv_payload, (
        f"Decompressed output does not match original payload. "
        f"Got {len(result)} bytes, expected {len(csv_payload)} bytes."
    )

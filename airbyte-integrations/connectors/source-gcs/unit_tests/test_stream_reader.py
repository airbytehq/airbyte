# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import datetime
import gzip
import io
from unittest.mock import MagicMock, Mock

import pytest
import pytz
from source_gcs import Config, SourceGCSStreamReader
from source_gcs.config import ServiceAccountCredentials
from source_gcs.helpers import GCSUploadableRemoteFile

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


def _make_mock_blob(bucket_name: str, blob_name: str) -> MagicMock:
    blob = MagicMock()
    blob.name = blob_name
    blob.bucket.name = bucket_name
    blob.updated = datetime.datetime.now(tz=pytz.utc)
    return blob


def test_get_matching_files_service_account_uses_gs_uri(logger):
    """Service Account auth must produce gs:// URIs so the CDK Parquet parser
    never sees signed-URL query parameters as Hive partition columns (issue #80940).

    displayed_uri is set to the canonical HTTPS path (no credentials, no query
    string) so the Cursor incremental state key is identical to the pre-fix
    behaviour — existing connections will not re-read already-synced files.
    """
    blob = _make_mock_blob("my-bucket", "data.csv")

    reader = SourceGCSStreamReader()
    reader._gcs_client = MagicMock()
    reader._gcs_client.get_bucket.return_value.list_blobs.return_value = [blob]
    reader._config = Config(
        credentials=ServiceAccountCredentials(service_account='{"type": "service_account"}', auth_type="Service"),
        bucket="my-bucket",
        streams=[],
    )

    files = list(reader.get_matching_files(["**/*.csv"], None, logger))

    assert len(files) == 1
    # gs:// URI — no query params — prevents spurious Parquet partition columns
    assert files[0].uri == "gs://my-bucket/data.csv"
    assert "X-Goog-Algorithm" not in files[0].uri
    blob.generate_signed_url.assert_not_called()
    # displayed_uri preserves the canonical HTTPS path used as the cursor state key
    assert files[0].displayed_uri == "https://storage.googleapis.com/my-bucket/data.csv"
    assert "X-Goog-Credential" not in files[0].displayed_uri
    assert "X-Goog-Signature" not in files[0].displayed_uri


def test_get_matching_files_service_account_percent_encodes_blob_name(logger):
    """Blob names with special characters must be percent-encoded in displayed_uri.

    generate_signed_url percent-encodes the resource path (safe="/~"), so the
    pre-fix cursor state key for a blob named e.g. "my file.parquet" was
    "https://storage.googleapis.com/bucket/my%20file.parquet". displayed_uri
    must match that encoding so existing incremental history is preserved.
    """
    blob = _make_mock_blob("my-bucket", "folder/my file #1.parquet")

    reader = SourceGCSStreamReader()
    reader._gcs_client = MagicMock()
    reader._gcs_client.get_bucket.return_value.list_blobs.return_value = [blob]
    reader._config = Config(
        credentials=ServiceAccountCredentials(service_account='{"type": "service_account"}', auth_type="Service"),
        bucket="my-bucket",
        streams=[],
    )

    files = list(reader.get_matching_files(["**/*.parquet"], None, logger))

    assert len(files) == 1
    assert files[0].uri == "gs://my-bucket/folder/my file #1.parquet"
    assert files[0].displayed_uri == "https://storage.googleapis.com/my-bucket/folder/my%20file%20%231.parquet"


def test_get_matching_files_oauth_uses_gs_uri(logger):
    """OAuth (Client) auth also produces gs:// URIs — unchanged by the fix."""
    from source_gcs.config import OAuthCredentials

    blob = _make_mock_blob("my-bucket", "data.csv")

    reader = SourceGCSStreamReader()
    reader._gcs_client = MagicMock()
    reader._gcs_client.get_bucket.return_value.list_blobs.return_value = [blob]
    reader._config = Config(
        credentials=OAuthCredentials(
            client_id="id",
            client_secret="secret",
            access_token="token",
            refresh_token="refresh",
            auth_type="Client",
        ),
        bucket="my-bucket",
        streams=[],
    )

    files = list(reader.get_matching_files(["**/*.csv"], None, logger))

    assert len(files) == 1
    assert files[0].uri == "gs://my-bucket/data.csv"


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

    assert (
        csv_payload.startswith(result) or result == csv_payload
    ), f"Decompressed output does not match original payload. Got {len(result)} bytes, expected {len(csv_payload)} bytes."


# ---------------------------------------------------------------------------
# Connector-level regression tests for Content-Encoding: gzip handling
# ---------------------------------------------------------------------------

_CSV_PAYLOAD = b"id,name,value\n1,Alice,100\n2,Bob,200\n3,Charlie,300\n"


def _make_gzip_encoded_file(uri: str, raw_bytes: bytes, content_encoding: str = "gzip") -> GCSUploadableRemoteFile:
    """Build a GCSUploadableRemoteFile with a mock blob that returns `raw_bytes` from `blob.open('rb', raw_download=True)`."""
    blob = MagicMock()
    blob.name = uri.split("/")[-1]
    blob.content_encoding = content_encoding
    blob.updated = datetime.datetime.now(tz=pytz.utc)
    blob.time_created = datetime.datetime.now(tz=pytz.utc)
    blob.id = "fake-id"
    blob.open.return_value = io.BytesIO(raw_bytes)

    file = GCSUploadableRemoteFile(
        uri=uri,
        blob=blob,
        last_modified=datetime.datetime.now(),
        mime_type="csv",
    )
    return file


@pytest.mark.parametrize(
    "raw_bytes,description",
    [
        pytest.param(
            gzip.compress(_CSV_PAYLOAD),
            "genuine gzip",
            id="genuine_gzip_content_encoding",
        ),
    ],
)
def test_open_gzip_encoded_blob_genuine(logger, raw_bytes, description):
    """Genuine gzip object with Content-Encoding: gzip is decompressed and readable.

    On master (without the fix), this code path goes through smart_open's
    default BlobReader with ranged downloads, which triggers
    'zlib.error: incorrect header check' due to GCS decompressive transcoding
    conflicts.  The fix bypasses smart_open for this case, using
    raw_download=True and gzip.GzipFile for streaming decompression.
    """
    file = _make_gzip_encoded_file("gs://bucket/test.csv", raw_bytes)
    reader = SourceGCSStreamReader()
    reader._gcs_client = MagicMock()
    reader._config = MagicMock()

    result = reader.open_file(file, FileReadMode.READ, "utf-8", logger)

    assert result.seekable(), "Stream should be seekable without full memory load"
    header = result.readline()
    assert header == "id,name,value\n"
    result.seek(0)
    full_content = result.read()
    assert full_content == _CSV_PAYLOAD.decode("utf-8")

    file.blob.open.assert_called_once_with("rb", raw_download=True)


def test_open_gzip_encoded_blob_mislabeled(logger):
    """Plain CSV with Content-Encoding: gzip (mislabeled) is read as plain text.

    The connector detects the missing gzip magic number and reads the raw
    bytes directly instead of attempting gzip decompression.
    """
    file = _make_gzip_encoded_file("gs://bucket/mislabeled.csv", _CSV_PAYLOAD)
    reader = SourceGCSStreamReader()
    reader._gcs_client = MagicMock()
    reader._config = MagicMock()

    result = reader.open_file(file, FileReadMode.READ, "utf-8", logger)

    assert result.seekable(), "Stream should be seekable without full memory load"
    header = result.readline()
    assert header == "id,name,value\n"
    result.seek(0)
    full_content = result.read()
    assert full_content == _CSV_PAYLOAD.decode("utf-8")


def test_open_gzip_encoded_blob_binary_mode(logger):
    """Content-Encoding: gzip blob opened in binary mode returns decompressed bytes."""
    compressed = gzip.compress(_CSV_PAYLOAD)
    file = _make_gzip_encoded_file("gs://bucket/binary.csv", compressed)
    reader = SourceGCSStreamReader()
    reader._gcs_client = MagicMock()
    reader._config = MagicMock()

    result = reader.open_file(file, FileReadMode.READ_BINARY, None, logger)

    content = result.read()
    assert content == _CSV_PAYLOAD


@pytest.mark.parametrize(
    "uri,content_encoding,mime_type",
    [
        pytest.param(
            "gs://bucket/normal.csv",
            None,
            "csv",
            id="no_content_encoding",
        ),
        pytest.param(
            "gs://bucket/data.csv.gz",
            "gzip",
            "csv.gz",
            id="gz_extension_uses_smart_open",
        ),
    ],
)
def test_open_file_does_not_use_raw_download(logger, uri, content_encoding, mime_type):
    """The raw_download gzip fix only activates for gs:// URIs with Content-Encoding: gzip
    and no .gz/.bz2 extension.  All other combinations take the standard smart_open path.
    """
    blob = MagicMock()
    blob.content_encoding = content_encoding

    file = MagicMock(spec=GCSUploadableRemoteFile)
    file.uri = uri
    file.blob = blob
    file.mime_type = mime_type

    reader = SourceGCSStreamReader()
    reader._gcs_client = MagicMock()
    reader._config = MagicMock()

    # smart_open returns a mock stream; the key assertion is that
    # blob.open(raw_download=True) is never used for these cases.
    reader.open_file(file, FileReadMode.READ, "utf-8", logger)

    blob.open.assert_not_called()


def test_https_uri_does_not_use_raw_download(logger):
    """HTTPS URIs bypass the Content-Encoding gzip fix (which only applies to gs://)."""
    blob = MagicMock()
    blob.content_encoding = "gzip"

    file = MagicMock(spec=GCSUploadableRemoteFile)
    file.uri = "https://storage.googleapis.com/bucket/file.csv"
    file.blob = blob
    file.mime_type = "csv"

    reader = SourceGCSStreamReader()
    reader._gcs_client = MagicMock()
    reader._config = MagicMock()

    # The HTTPS URI hits the real network, so smart_open raises OSError.
    # The key assertion is that blob.open(raw_download=True) is never called.
    with pytest.raises(OSError):
        reader.open_file(file, FileReadMode.READ, "utf-8", logger)

    blob.open.assert_not_called()

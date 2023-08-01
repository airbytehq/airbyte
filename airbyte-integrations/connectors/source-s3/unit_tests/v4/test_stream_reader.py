
import logging
from datetime import datetime
from itertools import product
from typing import Any, Dict, List, Optional, Set

import pytest
from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.exceptions import ErrorListingFiles, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_based_stream_reader import FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from botocore.stub import Stubber
from pydantic import AnyUrl
from source_s3.v4.config import Config
from source_s3.v4.stream_reader import SourceS3StreamReader

logger = logging.Logger("")

endpoint_values = ["http://fake.com", None]
_get_matching_files_cases = [
    pytest.param([], [], False, set(), id="no-files-match-if-no-globs"),
    pytest.param(
        ["**"],
        [
            {"Key": "file1.csv", "LastModified": datetime.now()},
            {"Key": "a/file2.csv", "LastModified": datetime.now()},
            {"Key": "a/b/file3.csv", "LastModified": datetime.now()},
            {"Key": "a/b/c/file4.csv", "LastModified": datetime.now()},
        ],
        False,
        {"file1.csv", "a/file2.csv", "a/b/file3.csv", "a/b/c/file4.csv"},
        id="all-files-match-single-page",
    ),
    pytest.param(
        ["**"],
        [
            {"Key": "file1.csv", "LastModified": datetime.now()},
            {"Key": "a/file2.csv", "LastModified": datetime.now()},
            {"Key": "a/b/file3.csv", "LastModified": datetime.now()},
            {"Key": "a/b/c/file4.csv", "LastModified": datetime.now()},
        ],
        True,
        {"file1.csv", "a/file2.csv", "a/b/file3.csv", "a/b/c/file4.csv"},
        id="all-files-match-multiple-pages",
    ),
    pytest.param(
        ["**/*.csv"],
        [
            {"Key": "file1.csv", "LastModified": datetime.now()},
            {"Key": "a/file2.csv", "LastModified": datetime.now()},
            {"Key": "a/b/file3.jsonl", "LastModified": datetime.now()},
            {"Key": "a/b/c/file4.jsonl", "LastModified": datetime.now()},
        ],
        True,
        {"file1.csv", "a/file2.csv"},
        id="nonmatching-files-are-filtered",
    ),
    pytest.param(
        ["a/*.csv", "a/*.jsonl"],
        [
            {"Key": "file1.csv", "LastModified": datetime.now()},
            {"Key": "file2.jsonl", "LastModified": datetime.now()},
            {"Key": "a/file3.csv", "LastModified": datetime.now()},
            {"Key": "a/file4.jsonl", "LastModified": datetime.now()},
        ],
        True,
        {"a/file3.csv", "a/file4.jsonl"},
        id="nonmatching-files-are-filtered-multiple-prefixes",
    ),
    pytest.param(
        ["**", "a/*.jsonl"],
        [
            {"Key": "file1.csv", "LastModified": datetime.now()},
            {"Key": "file2.jsonl", "LastModified": datetime.now()},
            {"Key": "a/file3.csv", "LastModified": datetime.now()},
            {"Key": "a/file4.jsonl", "LastModified": datetime.now()},
        ],
        True,
        {"file1.csv", "file2.jsonl", "a/file3.csv", "a/file4.jsonl"},
        id="files-matching-multiple-prefixes-only-listed-once",
    ),
    pytest.param(
        ["**"],
        [
            {"Key": "file1.csv", "LastModified": datetime.now()},
            {"Key": "file2.jsonl", "LastModified": datetime.now()},
            {"Key": "file3.csv", "LastModified": datetime.now()},
            {"Key": "file3.csv", "LastModified": datetime.now()},
        ],
        True,
        {"file1.csv", "file2.jsonl", "file3.csv"},
        id="duplicate-files-only-listed-once",
    ),
]

get_matching_files_cases = []
for original_case, endpoint_value in product(_get_matching_files_cases, endpoint_values):
    params = list(original_case.values) + [endpoint_value]
    test_case = pytest.param(*params, id=original_case.id + f"-endpoint-{endpoint_value}")
    get_matching_files_cases.append(test_case)


@pytest.mark.parametrize(
    "globs,mocked_response,multiple_pages,expected_uris,endpoint",
    get_matching_files_cases
)
def test_get_matching_files(globs: List[str], mocked_response: List[Dict[str, Any]], multiple_pages: bool, expected_uris: Set[str], endpoint: Optional[str]):
    reader = SourceS3StreamReader()
    try:
        aws_access_key_id = aws_secret_access_key = None if endpoint else "test"
        reader.config = Config(
            bucket="test",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            streams=[],
            endpoint=endpoint,
        )
    except Exception as exc:
        raise exc

    stub = set_stub(reader, mocked_response, multiple_pages)
    files = list(reader.get_matching_files(globs, logger))
    stub.deactivate()
    assert set(f.uri for f in files) == expected_uris


def test_get_matching_files_exception():
    reader = SourceS3StreamReader()
    reader.config = Config(bucket="test", aws_access_key_id="test", aws_secret_access_key="test", streams=[])
    stub = Stubber(reader.s3_client)
    stub.add_client_error("list_objects_v2")
    stub.activate()
    with pytest.raises(ErrorListingFiles) as exc:
        list(reader.get_matching_files(["*"], logger))
    stub.deactivate()
    assert FileBasedSourceError.ERROR_LISTING_FILES.value in exc.value.args[0]


def test_get_matching_files_without_config_raises_exception():
    with pytest.raises(ValueError):
        next(SourceS3StreamReader().get_matching_files([], logger))


def test_open_file_without_config_raises_exception():
    with pytest.raises(ValueError):
        with SourceS3StreamReader().open_file(RemoteFile(uri="", last_modified=datetime.now()), FileReadMode.READ, logger) as fp:
            fp.read()


def test_get_s3_client_without_config_raises_exception():
    with pytest.raises(ValueError):
        SourceS3StreamReader().s3_client


def test_cannot_set_wrong_config_type():
    stream_reader = SourceS3StreamReader()

    class OtherConfig(AbstractFileBasedSpec):
        def documentation_url(cls) -> AnyUrl:
            return AnyUrl("https://fake.com", scheme="https")

    other_config = OtherConfig(streams=[])
    with pytest.raises(AssertionError):
        stream_reader.config = other_config


def set_stub(reader: SourceS3StreamReader, contents: List[Dict[str, Any]], multiple_pages: bool) -> Stubber:
    s3_stub = Stubber(reader.s3_client)
    split_contents_idx = int(len(contents) / 2) if multiple_pages else -1
    page1, page2 = contents[:split_contents_idx], contents[split_contents_idx:]
    resp = {
        "KeyCount": len(page1),
        "Contents": page1,
    }
    if page2:
        resp["NextContinuationToken"] = "token"
    s3_stub.add_response("list_objects_v2", resp)
    if page2:
        s3_stub.add_response(
            "list_objects_v2",
            {
                "KeyCount": len(page2),
                "Contents": page2,
            },
        )
    s3_stub.activate()
    return s3_stub

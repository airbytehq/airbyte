#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from source_s3.v4 import SourceS3, SourceS3StreamReader
from source_s3.v4.entrypoint import SourceS3Entrypoint, launch

from airbyte_cdk.models import AirbyteMessageSerializer, FailureType, Status, Type
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


BUCKET_SECTION_CONFIG = {
    "check-section": "bucket",
    "bucket": "acme-exports",
    "credentials": {"auth_type": "iam_user", "aws_access_key_id": "key", "aws_secret_access_key": "secret"},
}

FULL_CONFIG = {
    "bucket": "acme-exports",
    "credentials": {"auth_type": "default_credentials"},
    "streams": [{"name": "exports", "format": {"filetype": "csv"}, "globs": ["**/*.csv"]}],
}


@pytest.fixture
def spec():
    return SourceS3.create().spec()


def test_validate_connection_accepts_the_partial_config_of_a_section(spec):
    SourceS3Entrypoint.validate_connection(spec, BUCKET_SECTION_CONFIG)


def test_validate_connection_still_validates_the_present_fields_of_a_section(spec):
    config = {**BUCKET_SECTION_CONFIG, "credentials": {"auth_type": "iam_user"}}

    with pytest.raises(AirbyteTracedException) as exc_info:
        SourceS3Entrypoint.validate_connection(spec, config)

    assert exc_info.value.failure_type == FailureType.config_error
    assert exc_info.value.message.startswith("Config validation error: ")


def test_validate_connection_requires_the_streams_for_the_files_section(spec):
    config = {**BUCKET_SECTION_CONFIG, "check-section": "files"}

    with pytest.raises(AirbyteTracedException) as exc_info:
        SourceS3Entrypoint.validate_connection(spec, config)

    assert "'streams' is a required property" in exc_info.value.message


def test_validate_connection_rejects_an_unknown_section(spec):
    with pytest.raises(AirbyteTracedException) as exc_info:
        SourceS3Entrypoint.validate_connection(spec, {**BUCKET_SECTION_CONFIG, "check-section": "nope"})

    assert exc_info.value.message == "Unknown check-section 'nope'; the connector specification declares: bucket, files, review."


def test_validate_connection_without_the_key_validates_the_full_spec(spec):
    SourceS3Entrypoint.validate_connection(spec, FULL_CONFIG)

    with pytest.raises(AirbyteTracedException) as exc_info:
        SourceS3Entrypoint.validate_connection(spec, {key: value for key, value in BUCKET_SECTION_CONFIG.items() if key != "check-section"})

    assert "'streams' is a required property" in exc_info.value.message


def _run_check(tmp_path, config, list_objects_v2):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    with patch.object(SourceS3StreamReader, "s3_client", new_callable=MagicMock) as s3_client:
        s3_client.list_objects_v2 = list_objects_v2
        entrypoint = SourceS3Entrypoint(SourceS3.create())
        messages = [
            AirbyteMessageSerializer.load(json.loads(line))
            for line in entrypoint.run(entrypoint.parse_args(["check", "--config", str(config_path)]))
        ]
    statuses = [message.connectionStatus for message in messages if message.type == Type.CONNECTION_STATUS]
    assert len(statuses) == 1, messages
    return statuses[0], s3_client


def test_check_of_the_bucket_section_lists_one_object_and_succeeds(tmp_path):
    status, s3_client = _run_check(tmp_path, BUCKET_SECTION_CONFIG, MagicMock(return_value={"KeyCount": 0}))

    assert status.status == Status.SUCCEEDED
    s3_client.list_objects_v2.assert_called_once_with(Bucket="acme-exports", MaxKeys=1)


def test_check_of_the_bucket_section_fails_on_a_missing_bucket(tmp_path):
    error = ClientError({"Error": {"Code": "NoSuchBucket", "Message": "The specified bucket does not exist"}}, "ListObjectsV2")

    status, _ = _run_check(tmp_path, BUCKET_SECTION_CONFIG, MagicMock(side_effect=error))

    assert status.status == Status.FAILED
    assert status.message == "The bucket acme-exports does not exist."


def test_check_of_the_bucket_section_fails_on_denied_access(tmp_path):
    error = ClientError({"Error": {"Code": "AccessDenied", "Message": "Access Denied"}}, "ListObjectsV2")

    status, _ = _run_check(tmp_path, BUCKET_SECTION_CONFIG, MagicMock(side_effect=error))

    assert status.status == Status.FAILED
    assert status.message == "Airbyte cannot list the bucket 'acme-exports' with the configured credentials: AccessDenied Access Denied"


def test_check_of_the_bucket_section_fails_on_an_unknown_section(tmp_path):
    status, s3_client = _run_check(tmp_path, {**BUCKET_SECTION_CONFIG, "check-section": "nope"}, MagicMock())

    assert status.status == Status.FAILED
    assert status.message == "Unknown check-section 'nope'; the connector specification declares: bucket, files, review."
    s3_client.list_objects_v2.assert_not_called()


def test_check_without_the_key_validates_the_full_spec(tmp_path):
    config = {key: value for key, value in FULL_CONFIG.items() if key != "bucket"}

    status, s3_client = _run_check(tmp_path, config, MagicMock())

    assert status.status == Status.FAILED
    assert "'bucket' is a required property" in status.message
    s3_client.list_objects_v2.assert_not_called()


def test_launch_runs_the_section_aware_entrypoint(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(BUCKET_SECTION_CONFIG))
    with patch.object(SourceS3StreamReader, "s3_client", new_callable=MagicMock) as s3_client, patch("builtins.print") as mock_print:
        s3_client.list_objects_v2 = MagicMock(return_value={"KeyCount": 0})
        launch(SourceS3.create(), ["check", "--config", str(config_path)])

    printed = [json.loads(call.args[0]) for call in mock_print.call_args_list if call.args and call.args[0].startswith("{")]
    statuses = [message["connectionStatus"] for message in printed if message["type"] == "CONNECTION_STATUS"]
    assert statuses == [{"status": "SUCCEEDED"}]

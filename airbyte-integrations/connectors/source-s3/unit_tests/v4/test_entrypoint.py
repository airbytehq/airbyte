#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""CHECK through the CDK entrypoint with the `check-section` key of the stepped setup form."""

import json
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError
from source_s3.v4 import SourceS3, SourceS3StreamReader

from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk.models import Status, Type


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


def _run_check(tmp_path, config, list_objects_v2):
    """Runs `check` end to end and returns the (status, message) of the CONNECTION_STATUS message and the S3 client mock."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    with patch.object(SourceS3StreamReader, "s3_client", new_callable=MagicMock) as s3_client:
        s3_client.list_objects_v2 = list_objects_v2
        entrypoint = AirbyteEntrypoint(SourceS3.create())
        messages = [json.loads(line) for line in entrypoint.run(entrypoint.parse_args(["check", "--config", str(config_path)]))]
    statuses = [message["connectionStatus"] for message in messages if message["type"] == Type.CONNECTION_STATUS.value]
    assert len(statuses) == 1, messages
    return (statuses[0]["status"], statuses[0].get("message")), s3_client


def test_check_of_the_bucket_section_lists_one_object_and_succeeds(tmp_path):
    status, s3_client = _run_check(tmp_path, BUCKET_SECTION_CONFIG, MagicMock(return_value={"KeyCount": 0}))

    assert status == (Status.SUCCEEDED.value, None)
    s3_client.list_objects_v2.assert_called_once_with(Bucket="acme-exports", MaxKeys=1)


def test_check_of_the_bucket_section_fails_on_a_missing_bucket(tmp_path):
    error = ClientError({"Error": {"Code": "NoSuchBucket", "Message": "The specified bucket does not exist"}}, "ListObjectsV2")

    status, _ = _run_check(tmp_path, BUCKET_SECTION_CONFIG, MagicMock(side_effect=error))

    assert status == (Status.FAILED.value, "The bucket acme-exports does not exist.")


def test_check_of_the_bucket_section_fails_on_denied_access(tmp_path):
    error = ClientError({"Error": {"Code": "AccessDenied", "Message": "Access Denied"}}, "ListObjectsV2")

    status, _ = _run_check(tmp_path, BUCKET_SECTION_CONFIG, MagicMock(side_effect=error))

    assert status == (
        Status.FAILED.value,
        "Airbyte cannot list the bucket 'acme-exports' with the configured credentials: AccessDenied Access Denied",
    )


def test_check_of_the_bucket_section_still_validates_the_present_fields(tmp_path):
    config = {**BUCKET_SECTION_CONFIG, "credentials": {"auth_type": "iam_user"}}

    status, s3_client = _run_check(tmp_path, config, MagicMock())

    assert status[0] == Status.FAILED.value
    assert status[1].startswith("Config validation error: ")
    s3_client.list_objects_v2.assert_not_called()


def test_check_of_the_files_section_requires_the_streams(tmp_path):
    config = {**BUCKET_SECTION_CONFIG, "check-section": "files"}

    status, s3_client = _run_check(tmp_path, config, MagicMock())

    assert status == (Status.FAILED.value, "Config validation error: 'streams' is a required property")
    s3_client.list_objects_v2.assert_not_called()


def test_check_of_an_unknown_section_fails(tmp_path):
    status, s3_client = _run_check(tmp_path, {**BUCKET_SECTION_CONFIG, "check-section": "nope"}, MagicMock())

    assert status == (
        Status.FAILED.value,
        "Unknown check-section 'nope'; the connector specification declares: bucket, files, review.",
    )
    s3_client.list_objects_v2.assert_not_called()


def test_check_of_the_review_section_is_rejected_as_it_has_no_check(tmp_path):
    config = {**FULL_CONFIG, "check-section": "review"}

    status, s3_client = _run_check(tmp_path, config, MagicMock())

    assert status == (
        Status.FAILED.value,
        "Section 'review' has no check: the connector specification does not declare \"check\": true for it.",
    )
    s3_client.list_objects_v2.assert_not_called()


def test_check_without_the_key_validates_the_full_spec(tmp_path):
    config = {key: value for key, value in FULL_CONFIG.items() if key != "bucket"}

    status, s3_client = _run_check(tmp_path, config, MagicMock())

    assert status == (Status.FAILED.value, "Config validation error: 'bucket' is a required property")
    s3_client.list_objects_v2.assert_not_called()

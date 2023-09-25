#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any

from airbyte_cdk import AirbyteLogger

from .integration_test import TestIncrementalFileStreamS3

LOGGER = AirbyteLogger()


def pytest_sessionfinish(session: Any, exitstatus: Any) -> None:
    """tries to find and remove all temp buckets"""
    instance = TestIncrementalFileStreamS3()
    instance._s3_connect(instance.credentials)
    temp_buckets = []
    for bucket in instance.s3_resource.buckets.all():
        if bucket.name.startswith(instance.temp_bucket_prefix):
            temp_buckets.append(bucket.name)
    for bucket_name in temp_buckets:
        bucket = instance.s3_resource.Bucket(bucket_name)
        bucket.objects.all().delete()
        bucket.delete()
        LOGGER.info(f"S3 Bucket {bucket_name} is now deleted")

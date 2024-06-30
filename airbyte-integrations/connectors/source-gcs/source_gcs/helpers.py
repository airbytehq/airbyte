#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json

from google.cloud import storage
from google.oauth2 import service_account


def get_gcs_client(config):
    credentials = service_account.Credentials.from_service_account_info(json.loads(config.service_account))
    client = storage.Client(credentials=credentials)
    return client


def get_gcs_blobs(config):
    client = get_gcs_client(config)
    bucket = client.get_bucket(config.gcs_bucket)
    blobs = bucket.list_blobs(prefix=config.gcs_path)
    # TODO: only support CSV initially. Change this check if implementing other file formats.
    blobs = [blob for blob in blobs if "csv" in blob.name.lower()]
    return blobs


def get_stream_name(blob):
    blob_name = blob.name
    # Remove path from stream name
    blob_name_without_path = blob_name.split("/")[-1]
    # Remove file extension from stream name
    stream_name = blob_name_without_path.replace(".csv", "")
    return stream_name

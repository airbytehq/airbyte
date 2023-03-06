#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io
import json

import pandas as pd
from google.cloud import storage
from google.cloud.storage.blob import Blob
from google.oauth2 import service_account


def get_gcs_client(config):
    credentials = service_account.Credentials.from_service_account_info(json.loads(config.get("service_account")))
    client = storage.Client(credentials=credentials)
    return client


def get_gcs_blobs(config):
    client = get_gcs_client(config)
    bucket = client.get_bucket(config.get("gcs_bucket"))
    blobs = bucket.list_blobs(prefix=config.get("gcs_path"))
    # TODO: only support CSV intially. Change this check if implementing other file formats.
    blobs = [blob for blob in blobs if "csv" in blob.name.lower()]
    return blobs


def read_csv_file(blob: Blob, limit_bytes=0):
    if limit_bytes:
        content = blob.download_as_bytes(start=0, end=limit_bytes)
    else:
        content = blob.download_as_bytes()
    bytes_buffer = io.BytesIO(content)
    df = pd.read_csv(bytes_buffer)
    return df


def construct_file_schema(df):
    # Fix all columns to string for maximum compability
    column_types = {col: "string" for col in df.columns}

    # Create a JSON schema object from the column data types
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {col: {"type": "string"} for col in df.columns},
    }
    return schema

def get_stream_name(blob):
    blob_name = blob.name
    # Remove path from stream name
    blob_name_without_path = blob_name.split('/')[-1]
    # Remove file extension from stream name
    stream_name = blob_name_without_path.replace(".csv", "")
    return stream_name

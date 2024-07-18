# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from io import BytesIO

from google.cloud import storage


def download_blob_into_memory(bucket_name, blob_name):
    # Initialize a client
    client = storage.Client()

    # Get the bucket and blob
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Download the blob's content into memory
    content = blob.download_as_bytes()

    # If you want to use a file-like object, you can use BytesIO
    file_like_object = BytesIO(content)

    return file_like_object

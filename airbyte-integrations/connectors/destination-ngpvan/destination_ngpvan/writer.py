#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.

import csv
import datetime
from collections import Mapping
from google.cloud import storage
from destination_ngpvan.client import NGPVANClient

import os #only needed for local development

class NGPVANWriter:
    """
    This class is used to create the "writer" object in destination.py
    It initializes using the VGPVANClient class, which will eventually include API methods but doesn't do anything yet except to receive the VAN API key
    """

    data_output = []

    def __init__(self, client: NGPVANClient):
        self.client = client
        self.local_test = client.local_test
        self.output_file_name = "output_airbyte.csv" #TODO parameterize this and add timestamp
        self.destination_bucket = "vansync-testing" #TODO parameterize this

    def add_data_row(self, record: Mapping):
        """Adds a record (from the AirbyteMessage stream) to the data_output list."""
        new_row={}
        for col in record:
            field_name = col
            value = record[col]
            new_row[field_name]=value
        self.data_output.append(new_row)

    def write_to_local_csv(self):
        """Writes the data_output list to a CSV."""
        keys = self.data_output[0].keys()
        output_file = open(self.output_file_name, "w")
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(self.data_output)
        output_file.close()

    def upload_output_to_gcs(self):
        """Uploads the output CSV to GCS."""

        if self.local_test:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/google_credentials_file.json"

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.destination_bucket)
        blob = bucket.blob(self.output_file_name)
        blob.upload_from_filename(self.output_file_name)
        print('File {} uploaded to {}.'.format(
            self.output_file_name,
            self.destination_bucket))

    def generate_download_signed_url_v4(self):
        """Generates a v4 signed URL for downloading a blob.

        bucket_name = 'your-bucket-name'
        blob_name = 'your-object-name'

        Note that this method requires a service account key file. You can not use
        this if you are using Application Default Credentials from Google Compute
        Engine or from the Google Cloud SDK.
        """

        if self.local_test:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/google_credentials_file.json"

        bucket_name = self.output_file_name
        blob_name = self.destination_bucket
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            # This URL is valid for 15 minutes
            expiration=datetime.timedelta(minutes=15),
            # Allow GET requests using this URL.
            method="GET",
        )

        return url

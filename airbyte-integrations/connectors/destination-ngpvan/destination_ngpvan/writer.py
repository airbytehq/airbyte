#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.

from zipfile import ZipFile
import csv
import datetime
import time
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
        self.client=client
        self.local_test=client.local_test
        self.destination_bucket = client.gcs_bucket
        self.timestamp_milliseconds=str(int(round(time.time() * 1000)))
        self.output_blob_name = "output_airbyte_compressed_"+self.timestamp_milliseconds
        self.csv_name=self.output_blob_name+'.csv'
        self.zip_name=self.output_blob_name+'.zip'

    def add_data_row(self, record: Mapping):
        """Adds a record (from the AirbyteMessage stream) to the data_output list."""
        new_row={}
        for col in record:
            field_name = col
            value = record[col]
            new_row[field_name]=value
        self.data_output.append(new_row)

    def _write_to_local_csv(self):
        """Writes the data_output list to a zip-compressed CSV."""
        keys=self.data_output[0].keys()
        with open(self.csv_name, "w") as csvfile:
            csv_writer = csv.DictWriter(csvfile, keys)
            csv_writer.writeheader()
            csv_writer.writerows(self.data_output)
            csvfile.close()

        #write the csv to a ZIP file (required by VAN's API)
        zipObj = ZipFile(self.zip_name, 'w')
        zipObj.write(self.csv_name)
        zipObj.close()

    def _upload_csv_to_gcs(self):
        """Uploads the output ZIP to GCS."""

        if self.local_test:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/google_credentials_file.json"
        elif self.client.service_account_key:
            try:
                keyfile='credentials.json'
                with open(keyfile, "w") as secret_file:
                    secret_file.write(self.client.service_account_key)
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=keyfile
            except:
                print("Failed to write service account keyfile. RIP")

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.destination_bucket)
        blob = bucket.blob(self.zip_name)
        blob.upload_from_filename(self.zip_name)
        print('File {} uploaded to {}.'.format(
            self.zip_name,
            self.destination_bucket))

    def _generate_download_signed_url_v4(self):
        """Generates a v4 signed URL for downloading a blob.

        bucket_name = 'your-bucket-name'
        blob_name = 'your-object-name'

        Note that this method requires a service account key file. You can not use
        this if you are using Application Default Credentials from Google Compute
        Engine or from the Google Cloud SDK.
        """

        if self.local_test:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/google_credentials_file.json"

        bucket_name = self.destination_bucket
        blob_name = self.zip_name
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

    def run_bulk_import_job(self):
        "Run the bulk import job specified in the destination config"

        self._write_to_local_csv()
        self._upload_csv_to_gcs()

        fileName=self.csv_name
        columns=self.data_output[0].keys()
        sourceUrl = self._generate_download_signed_url_v4()

        print(f'sourceUrl: {sourceUrl}')

        if self.client.bulk_import_type == "Contacts":
            r=self.client.bulk_upsert_contacts(fileName=fileName,columns=columns,sourceUrl=sourceUrl)
        elif self.client.bulk_import_type == "Activist Codes":
            r=self.client.bulk_apply_activist_codes(fileName=fileName, columns=columns, sourceUrl=sourceUrl)
        else:
            return "The selected bulk import type is not supported"

        return r.json()["jobId"]

#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.

from zipfile import ZipFile
import csv
import datetime
import logging
import pandas as pd
import ssl
import time
import wget
from collections import Mapping
from google.cloud import storage
from destination_ngpvan.client import NGPVANClient

import os

class NGPVANWriter:
    """
    This class is used to create the "writer" object in destination.py
    It initializes using the VGPVANClient class, which will eventually include API methods but doesn't do anything yet except to receive the VAN API key
    """

    data_output=[]

    def __init__(self, client: NGPVANClient):
        self.client=client
        self.local_test=client.local_test
        self.destination_bucket=client.gcs_bucket
        self.timestamp_milliseconds=str(int(round(time.time() * 1000)))
        self.data_csv_name="data_import.csv"
        self.data_zip_name="data_import.zip"
        self.data_blob_name=self.timestamp_milliseconds+"/"+self.data_zip_name
        self.results_full_blob_name=self.timestamp_milliseconds+"/results_full.csv"
        self.results_summary_name="results_summary.csv"
        self.results_summary_blob_name=self.timestamp_milliseconds+"/results_summary.csv"
        self.timeout=3600 #seconds Airbyte will spend polling for job status

    def add_data_row(self, record: Mapping):
        """Adds a record (from the AirbyteMessage stream) to the data_output list."""
        new_row={}
        for col in record:
            field_name=col
            value=record[col]
            new_row[field_name]=value
        self.data_output.append(new_row)

    def _write_to_local_csv(self):
        """Writes the data_output list to a zip-compressed CSV."""
        keys=self.data_output[0].keys()
        with open(self.data_csv_name, "w") as csvfile:
            csv_writer=csv.DictWriter(csvfile, keys)
            csv_writer.writeheader()
            csv_writer.writerows(self.data_output)
            csvfile.close()

        #write the csv to a ZIP file (required by VAN's API)
        zipObj=ZipFile(self.data_zip_name, 'w')
        zipObj.write(self.data_csv_name)
        zipObj.close()

    def _upload_csv_to_gcs(self):
        """Uploads the output ZIP to GCS."""

        if self.local_test:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="secrets/google_credentials_file.json"
        elif self.client.service_account_key:
            try:
                keyfile='credentials.json'
                with open(keyfile, "w") as secret_file:
                    secret_file.write(self.client.service_account_key)
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=keyfile
            except:
                print("Failed to write service account keyfile. RIP")

        storage_client=storage.Client()
        bucket=storage_client.get_bucket(self.destination_bucket)
        blob=bucket.blob(self.data_blob_name)
        blob.upload_from_filename(self.data_zip_name)
        print('File {} uploaded to {}.'.format(
            self.data_zip_name,
            self.destination_bucket))

    def _generate_download_signed_url_v4(self):
        """Generates a v4 signed URL for downloading a blob.

        bucket_name='your-bucket-name'
        blob_name='your-object-name'

        Note that this method requires a service account key file. You can not use
        this if you are using Application Default Credentials from Google Compute
        Engine or from the Google Cloud SDK.
        """

        if self.local_test:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="secrets/google_credentials_file.json"

        bucket_name=self.destination_bucket
        blob_name=self.data_blob_name
        storage_client=storage.Client()
        bucket=storage_client.bucket(bucket_name)
        blob=bucket.blob(blob_name)

        url=blob.generate_signed_url(
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

        fileName=self.data_csv_name
        columns=self.data_output[0].keys()
        sourceUrl=self._generate_download_signed_url_v4()

        print(f'sourceUrl: {sourceUrl}')

        if self.client.bulk_import_type == "Contacts":
            r=self.client.bulk_upsert_contacts(fileName=fileName,columns=columns,sourceUrl=sourceUrl)
        elif self.client.bulk_import_type == "Activist Codes":
            r=self.client.bulk_apply_activist_codes(fileName=fileName, columns=columns, sourceUrl=sourceUrl)
        else:
            return "The selected bulk import type is not supported"

        return str(r.json()["jobId"])

    def monitor_bulk_import_status(self, job_id: str):
        """Checks the bulk import job status every 5 minutes and returns the URL to the results file once complete"""

        start_import_time=time.perf_counter()

        status=""
        time_elapsed=0
        logMessage=f"Keeping an eye on bulk import job #{job_id}..."
        logging.info(logMessage)

        while status!="Completed" and time_elapsed<self.timeout:
            time.sleep(5)
            status_json=self.client.get_bulk_import_job_status(job_id)
            status=status_json["status"]
            time_elapsed=round(time.perf_counter()-start_import_time)
            logMessage=f"Job status: {status} (time elapsed: {time_elapsed} seconds)"
            logging.info(logMessage)

            if status=="Error" or status=="Failed":
                logMessage=f"Bulk import failed with error. Here is the full status response: {status_json}"
                logging.info(logMessage)
                return None

        if status=="Completed":
            results_url=status_json["resultFiles"][0]["url"]
            logMessage=f"Bulk import complete. Results file located at: {results_url}"
            logging.info(logMessage)
            return results_url

        elif time_elapsed>=self.timeout:
            logMessage="""
            The bulk import job is taking a really long time. This might be caused by a very large import or heavy traffic on VAN servers.
            Airbyte is going to stop watching, but you can check on the status of the job here: https://app.ngpvan.com/BulkUploadBatchesList.aspx
            """
            logging.info(logMessage)
            return None


    def upload_file_url_to_gcs(self, source_file_url: str):
        """
        Upload file from a URL to GCS

        Usage: send the results file URL returned by VAN API to GCS
        """

        if self.local_test:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="secrets/google_credentials_file.json"

        bucket_name=self.destination_bucket
        blob_name=self.results_full_blob_name
        storage_client=storage.Client()

        logging.info(f"Sending the bulk import results file to GCS...")

        # Download the file to local disk
        # TODO() make sure this isn't a spooky thing to do
        ssl._create_default_https_context=ssl._create_unverified_context
        local_results_csv_filename=wget.download(source_file_url)

        # Send the file to GCS
        bucket=storage_client.get_bucket(bucket_name)
        blob=bucket.blob(blob_name)
        blob.upload_from_filename(local_results_csv_filename)

        logging.info(f"Results file successfully uploaded to {bucket_name}/{blob_name}.")

        return local_results_csv_filename

    def summarize_bulk_import(self, file_path: str):
        """
        Write a summary of the results of the bulk import job to a CSV in GCS
        """

        logging.info("Sending a results summary to GCS...")

        # Create a pandas dataframe with a row count summary for different outcomes
        df=pd.read_csv(file_path)
        last_column=df.iloc[:, -1] # The last column says whether each row imported successfully or threw an error
        counts_df=last_column.value_counts(ascending=False).rename_axis('bulk_import_result').reset_index(name='number_of_records')

        logging.info("VAN bulk import job completed with the following results:")
        for index, row in counts_df.iterrows():
            nrecords=row['number_of_records']
            result=row['bulk_import_result']
            logging.info((f"{result}: {nrecords}")

        # Write the dataframe to a csv
        summary_filename=self.results_summary_name
        counts_df.to_csv(summary_filename)

        # Send the CSV to GCS
        if self.local_test:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="secrets/google_credentials_file.json"

        bucket_name=self.destination_bucket
        blob_name=self.results_summary_blob_name
        storage_client=storage.Client()

        bucket=storage_client.get_bucket(bucket_name)
        blob=bucket.blob(blob_name)
        blob.upload_from_filename(summary_filename)

        logging.info(f"Summary written to GCS at {bucket_name}/{blob_name}")

        return True

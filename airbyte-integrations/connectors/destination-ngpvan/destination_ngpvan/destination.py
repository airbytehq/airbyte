#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
# Airbyte Destination: NGPVAN
# Author: Emily Cogsdill
# Date: February 2022
# This destination sends data to VAN using the API's bulk import endpoint.
# Import modes supported: Contacts, Activist Codes

"""
TODO()
- stress test larger imports (querying a 180k row table seems like too much, but 10k is fine; what should we expect partners to need to do?)
- any sources we should test besides BQ and Sheets? maybe GCS?

Maybe post MVP:
- ENABLE DBT? is that hard?
- need to parse source data (from AirbyteMessage) to conform to format required by VAN API
- support additional bulk import operations
- support import from multiple streams in the same Airbyte sync (this will take some doing)
"""

import logging
import os
from google.cloud import storage
from typing import Mapping, Any, Iterable

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from destination_ngpvan.client import NGPVANClient
from destination_ngpvan.writer import NGPVANWriter

class DestinationNGPVAN(Destination):

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        """
        Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received
        in the input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been
        successfully persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.

        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the
                                    destination
        :param input_messages: The stream of input messages received from the source
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """

        logging.getLogger().setLevel(logging.INFO)
        writer = NGPVANWriter(NGPVANClient(**config))


        logging.info(f"Reading data from source...")

        for message in input_messages:
            if message.type == Type.RECORD:
                record = message.record
                data_row = record.data
                writer.add_data_row(data_row)
                yield message
            else:
                continue

        logging.info(f"Data successfully read from source.")

        job_id=writer.run_bulk_import_job()

        print(f'Successfully created VAN bulk import job (ID: {job_id})')

        results_file_url=writer.monitor_bulk_import_status(job_id=job_id)

        if results_file_url:
            results_file_local_path=writer.upload_file_url_to_gcs(results_file_url)
            writer.summarize_bulk_import(results_file_local_path)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:

            writer = NGPVANWriter(NGPVANClient(**config))

            #Validate VAN API key
            writer.client.get_mappings()

            #Try connecting to GCS
            if writer.local_test:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/google_credentials_file.json"

            bucket_name = writer.destination_bucket
            blob_name = writer.zip_name
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")




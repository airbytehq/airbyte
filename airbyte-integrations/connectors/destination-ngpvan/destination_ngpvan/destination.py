#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
# Airbyte Destination: NGPVAN
# Author: Emily Cogsdill
# Date: February 2022
# This destination sends data to VAN using the API's bulk import endpoint.

"""
REQUIREMENTS FOR USING THIS CONNECTOR (2/10/22):
--aka known limitations--
*This connector supports two types of bulk imports: Contacts and Activist Codes.
*Result file sizes are capped at 100MB.
*This connector does not break up large jobs to ensure that the result files will be within the 100MB limit.
*We assume the columns from the source are already named in the way VAN API requires.

TODO()
- chunk import files into predefined sizes and send them all as distinct jobs within the same POST request
- write results file and summary to bigquery
- do some column renaming (eg with fuzzy matching) to make source data schema a little more flexible
- ENABLE DBT? is that hard?
- additional bulk import operations (depending on common use cases)
- support import from multiple streams in the same Airbyte sync
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
        logging.info(f'Successfully created VAN bulk import job (ID: {job_id})')

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
            blob_name = writer.data_zip_name
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")




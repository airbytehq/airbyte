#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
# Airbyte Destination: NGPVAN
# Author: Emily Cogsdill
# Date: February 2022
# This destination sends data to VAN using the API's bulk import endpoint.
# Import modes supported: Contacts, Activist Codes
# The implementation of the VAN API borrows heavily from parsons: https://github.com/move-coop/parsons/tree/master/parsons/ngpvan

"""
TODO()
- test the Activist Codes import a bit more to make sure it's doing the thing
- ask airbyte about waiting for job status? what is bp?
- add a time.sleep(5) and check job status; throw an error if job has failed (return the text from the job status endpoint)
- need to parse source data (from AirbyteMessage) to conform to format required by VAN API
- ENABLE DBT? is that hard?
- test different data sources (Sheets, BQ, GCS, any others?) to make sure the connector still works
- support additional bulk import operations
- test larger files? can we generate larger amounts of synthetic data using Hudson's strats?
- what user stories are we still missing after all this?ping import Mapping, Any, Iterable
"""
import time
from typing import Mapping, Any, Iterable

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from destination_ngpvan.client import NGPVANClient
from destination_ngpvan.writer import NGPVANWriter
from destination_ngpvan.validator import NGPVANValidator

class DestinationNGPVAN(Destination):

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:

        writer = NGPVANWriter(NGPVANClient(**config))

        for message in input_messages:
            # Adds data rows from RECORD messages in the AirbyteMessage to the writer object
            if message.type == Type.RECORD:
                record = message.record
                data_row = record.data
                writer.add_data_row(data_row)
                yield message
            else:
                # ignore other message types for now
                continue

        jobId=str(writer.run_bulk_import_job())

        print(f'Bulk import job created: ID {jobId}')

        validator=NGPVANValidator(client=NGPVANClient(**config),jobId=jobId)
        validator.monitorBulkImportStatus()

        #start_import_time=time.perf_counter()
#
        #status=""
        #print("Keeping an eye on it...")
        #while status!="Completed":
        #    time.sleep(5)
        #    status_json=writer.client.get_bulk_import_job_status(str(jobId))
        #    status=status_json["status"]
        #    time_elapsed=round(time.perf_counter()-start_import_time)
        #    print(f"Job status: {status} (time elapsed: {time_elapsed} seconds)")
#
        #    if status=="Error":
        #        print("Bulk import failed with error. Here is the full status response:")
        #        print(status_json)
        #        break
#
        #results_url=status_json["resultFiles"][0]["url"]
        #print(f"Bulk import complete. Results file located at: {results_url}")

        """
        TODO
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
            # TODO

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")




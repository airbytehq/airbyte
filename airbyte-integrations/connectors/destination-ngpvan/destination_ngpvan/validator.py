# Copyright (c) 2022 Airbyte, Inc., all rights reserved.

import logging
import time
from destination_ngpvan.client import NGPVANClient

class NGPVANValidator:
    """
    TODO() write something useful here
    TODO() will eventually use this object to run fancier validation? Like by reading the file from the results url?
    """

    logging.getLogger().setLevel(logging.INFO)

    def __init__(self, client: NGPVANClient, jobId: str):
        self.client=client
        self.jobId=jobId
        self.timeout=3600 #seconds Airbyte will spend polling for job status

    def monitorBulkImportStatus(self):
        """Checks the bulk import job status every 5 minutes and returns the URL to the results file once complete"""

        start_import_time=time.perf_counter()

        status=""
        time_elapsed=0
        logMessage=f"Keeping an eye on bulk import job #{self.jobId}..."
        logging.info(logMessage)

        while status!="Completed" and time_elapsed<self.timeout:
            time.sleep(5)
            status_json=self.client.get_bulk_import_job_status(self.jobId)
            status=status_json["status"]
            time_elapsed=round(time.perf_counter()-start_import_time)
            logMessage=f"Job status: {status} (time elapsed: {time_elapsed} seconds)"
            logging.info(logMessage)

            if status=="Error":
                logMessage=f"Bulk import failed with error. Here is the full status response: {status_json}"
                logging.info(logMessage)
                break

        if status=="Completed":
            results_url=status_json["resultFiles"][0]["url"]
            logMessage=f"Bulk import complete. Results file located at: {results_url}"
            logging.info(logMessage)
            return results_url

        elif time_elapsed>=self.timeout:
            logMessage=f"Import taking too long (VAN might still be processing it, but Airbyte isn't watching anymore)"
            logging.info(logMessage)
            return None


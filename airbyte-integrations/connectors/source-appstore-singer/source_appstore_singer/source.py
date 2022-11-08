#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from datetime import date, timedelta
from typing import Dict

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.models.airbyte_protocol import AirbyteConnectionStatus
from airbyte_cdk.sources.singer.singer_helpers import SyncModeInfo
from airbyte_cdk.sources.singer.source import SingerSource
from appstoreconnect import Api


class SourceAppstoreSinger(SingerSource):
    TAP_CMD = "tap-appstore"

    def check_config(self, logger: AirbyteLogger, config_path: str, config: json) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration
            e.g: if a provided Stripe API token can be used to connect to the Stripe API.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config_path: Path to the file containing the configuration json config
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            # If an app on the appstore does not support subscriptions or sales, it cannot pull the relevant reports.
            # However, the way the Appstore API expresses this is not via clear error messages. Instead it expresses it by throwing an unrelated
            # error, in this case "invalid vendor ID". There is no way to distinguish if this error is due to invalid credentials or due to
            # the account not supporting this kind of report. So to "check connection" we see if any of the reports can be pulled and if so
            # return success. If no reports can be pulled we display the exception messages generated for all reports and return failure.
            api_fields_to_test = {
                "subscription_event_report": {
                    "reportType": "SUBSCRIPTION_EVENT",
                    "frequency": "DAILY",
                    "reportSubType": "SUMMARY",
                    "version": "1_2",
                },
                "subscriber_report": {"reportType": "SUBSCRIBER", "frequency": "DAILY", "reportSubType": "DETAILED", "version": "1_2"},
                "subscription_report": {"reportType": "SUBSCRIPTION", "frequency": "DAILY", "reportSubType": "SUMMARY", "version": "1_2"},
                "sales_report": {"reportType": "SALES", "frequency": "DAILY", "reportSubType": "SUMMARY", "version": "1_0"},
            }

            api = Api(config["key_id"], config["key_file"], config["issuer_id"])
            stream_to_error = {}
            for stream, params in api_fields_to_test.items():
                test_date = date.today() - timedelta(days=2)
                report_filters = {"reportDate": test_date.strftime("%Y-%m-%d"), "vendorNumber": f"{config['vendor']}"}
                report_filters.update(api_fields_to_test[stream])
                try:
                    rep_tsv = api.download_sales_and_trends_reports(filters=report_filters)
                    if isinstance(rep_tsv, dict):
                        raise Exception(f"An exception occurred: Received a JSON response instead of" f" the report: {str(rep_tsv)}")
                except Exception as e:
                    logger.warn(f"Unable to download {stream}: {e}")
                    stream_to_error[stream] = e

            # All streams have failed
            if len(stream_to_error.keys()) == api_fields_to_test.keys():
                message = "\n".join([f"Unable to access {stream} due to error: {e}" for stream, e in stream_to_error])
                return AirbyteConnectionStatus(status=Status.FAILED, message=message)

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.warn(e)
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        """
        Return the string commands to invoke the tap with the --discover flag and the right configuration options
        """
        return f"{self.TAP_CMD} -c {config_path} --discover"

    def read_cmd(self, logger: AirbyteLogger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        """
        Return the string commands to invoke the tap with the right configuration options to read data from the source
        """
        config_option = f"--config {config_path}"
        properties_option = f"--properties {catalog_path}"
        state_option = f"--state {state_path}" if state_path else ""
        return f"{self.TAP_CMD} {config_option} {properties_option} {state_option}"

    def transform_config(self, raw_config: json) -> json:
        """
        Return the string commands to invoke the tap with the right configuration options to read data from the source
        """
        # path where we will write the private key.
        keyfile_path = "/tmp/keyfile.p8"

        # write the private key to a file.
        private_key = raw_config["private_key"]
        with open(keyfile_path, "w") as fh:
            fh.write(private_key)

        # add the path of the key file in he config for tap-appstore to use.
        raw_config["key_file"] = keyfile_path

        # remove private_key because we shouldn't need it for anything else in the config.
        del raw_config["private_key"]

        return raw_config

    def get_sync_mode_overrides(self) -> Dict[str, SyncModeInfo]:
        streams = ["sales_report", "subscriber_report", "subscription_report", "subscription_event_report"]
        return {s: SyncModeInfo(supported_sync_modes=[SyncMode.incremental], source_defined_cursor=True) for s in streams}

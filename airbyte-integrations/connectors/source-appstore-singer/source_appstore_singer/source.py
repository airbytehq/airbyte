"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from datetime import date, timedelta

from airbyte_protocol import AirbyteConnectionStatus
from appstoreconnect import Api
from base_python import AirbyteLogger
from base_singer import SingerSource, Status


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
            # create request fields for testing
            api_fields_to_test = {
                "subscription_report": {"reportType": "SUBSCRIPTION", "frequency": "DAILY", "reportSubType": "SUMMARY", "version": "1_2"}
            }
            test_date = date.today() - timedelta(days=2)
            report_filters = {"reportDate": test_date.strftime("%Y-%m-%d"), "vendorNumber": "{}".format(config["vendor"])}

            report_filters.update(api_fields_to_test["subscription_report"])

            # fetch data from appstore api
            api = Api(config["key_id"], config["key_file"], config["issuer_id"])

            rep_tsv = api.download_sales_and_trends_reports(filters=report_filters)

            if isinstance(rep_tsv, dict):
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message=f"An exception occurred: Received a JSON response instead of" f" the report: {str(rep_tsv)}",
                )

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

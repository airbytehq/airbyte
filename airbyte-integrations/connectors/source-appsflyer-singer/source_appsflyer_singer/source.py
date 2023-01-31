#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from datetime import date, timedelta

import requests
from airbyte_protocol import AirbyteConnectionStatus
from base_python import AirbyteLogger
from base_singer import SingerSource, Status


class SourceAppsflyerSinger(SingerSource):
    TAP_CMD = "tap-appsflyer"

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
            test_date = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M")
            params = {"from": test_date, "to": test_date, "api_token": config["api_token"]}

            base_url = "https://hq.appsflyer.com"
            test_endpoint = "/export/{}/installs_report/v5".format(config["app_id"])

            url = base_url + test_endpoint

            logger.info("GET {}".format(url))
            resp = requests.get(url, params=params)

            if resp.status_code == 200:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message=f"An exception occurred: Status Code: {0}, content: {1}".format(resp.status_code, resp.content),
                )
        except Exception as e:
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

#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from airbyte_cdk.sources.singer import SingerSource


class SourceKustomerSinger(SingerSource):
    TAP_CMD = "tap-kustomer"

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
        url = "https://api.kustomerapp.com/v1/customers"
        headers = {"Authorization": f"Bearer {config['api_token']}"}

        try:
            session = requests.get(url, headers=headers)
            session.raise_for_status()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except requests.exceptions.RequestException as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")

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
        properties_option = f"--catalog {catalog_path}"
        state_option = f"--state {state_path}" if state_path else ""
        return f"{self.TAP_CMD} {config_option} {properties_option} {state_option}"

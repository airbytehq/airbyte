#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from airbyte_cdk.sources.singer import SingerSource
from requests_oauthlib import OAuth2Session
from tap_quickbooks.client import PROD_ENDPOINT_BASE, SANDBOX_ENDPOINT_BASE, TOKEN_REFRESH_URL


class SourceQuickbooksSinger(SingerSource):
    TAP_CMD = "tap-quickbooks"

    def _write_config(self, token):
        logger = AirbyteLogger()
        logger.info("Credentials Refreshed")

    def check_config(self, logger: AirbyteLogger, config_path: str, config: json) -> AirbyteConnectionStatus:
        token = {"refresh_token": config["refresh_token"], "token_type": "Bearer", "access_token": "wrong", "expires_in": "-30"}
        extra = {"client_id": config["client_id"], "client_secret": config["client_secret"]}

        sandbox = bool(config.get("sandbox", False))

        user_agent = config["user_agent"]
        realm_id = config["realm_id"]
        session = OAuth2Session(
            config["client_id"],
            token=token,
            auto_refresh_url=TOKEN_REFRESH_URL,
            auto_refresh_kwargs=extra,
            token_updater=self._write_config,
        )

        endpoint = f"/v3/company/{realm_id}/query"
        params = {"query": "SELECT * FROM CompanyInfo"}
        headers = {"Accept": "application/json", "User-Agent": user_agent}

        if sandbox:
            full_url = SANDBOX_ENDPOINT_BASE + endpoint
        else:
            full_url = PROD_ENDPOINT_BASE + endpoint

        try:
            session.request("GET", full_url, headers=headers, params=params)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        return f"{self.TAP_CMD} --config {config_path} --discover"

    def read_cmd(self, logger: AirbyteLogger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        config_option = f"--config {config_path}"
        properties_option = f"--catalog {catalog_path}"
        state_option = f"--state {state_path}" if state_path else ""
        return f"{self.TAP_CMD} {config_option} {properties_option} {state_option}"

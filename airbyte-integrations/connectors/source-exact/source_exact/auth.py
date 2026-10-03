# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

from airbyte_cdk import SingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime
from source_exact.utils_func import is_dev


HERE = Path(__file__).parent


class ExactOauth2Authenticator(SingleUseRefreshTokenOauth2Authenticator):
    """
    This class
        - overrides some methods to updat the local config file during development.
        - the airbyte_cdk library from the implementation for this connector
    """

    def __init__(self, connector_config, token_refresh_endpoint, **kwargs):
        super().__init__(connector_config, token_refresh_endpoint, **kwargs)

    def set_refresh_token(self, new_refresh_token: str) -> None:
        super().set_refresh_token(new_refresh_token=new_refresh_token)
        if is_dev():
            # Update local secrets file

            with open(HERE.parent / "secrets/config.json", "r") as file:
                file_data = json.loads(file.read())

            file_data["credentials"]["refresh_token"] = new_refresh_token

            with open(HERE.parent / "secrets/config.json", "w") as file:
                file.write(json.dumps(file_data, indent=2))

    def get_access_token(self) -> str:
        access_token = super().get_access_token()
        if is_dev():
            # Update local secrets file

            with open(HERE.parent / "secrets/config.json", "r") as file:
                file_data = json.loads(file.read())

            file_data["credentials"]["access_token"] = access_token

            with open(HERE.parent / "secrets/config.json", "w") as file:
                file.write(json.dumps(file_data, indent=2))
        return self.access_token

    def set_token_expiry_date(self, new_token_expiry_date: AirbyteDateTime) -> None:
        super().set_token_expiry_date(new_token_expiry_date=new_token_expiry_date)
        if is_dev():
            with open(HERE.parent / "secrets/config.json", "r") as file:
                file_data = json.loads(file.read())

            file_data["credentials"]["token_expiry_date"] = str(new_token_expiry_date)

            with open(HERE.parent / "secrets/config.json", "w") as file:
                file.write(json.dumps(file_data, indent=2))

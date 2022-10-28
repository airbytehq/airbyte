#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import base64
import json
import os
import re
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, ClassVar, Mapping, Tuple

from ci_common_utils import GoogleApi, Logger

DEFAULT_SECRET_FILE = "config"
DEFAULT_SECRET_FILE_WITH_EXT = DEFAULT_SECRET_FILE + ".json"

GSM_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)

MASK_KEY_PATTERNS = [
    "password",
    "host",
    "user",
    "_key",
    "_id",
    "token",
    "secret",
    "bucket",
    "role_arn",
    "service_account_info",
    "account_id",
    "api",
    "domain_url",
    "client_id",
    "access",
    "jwt",
    "base_url",
    "key",
    "credentials",
    "_sid",
    "survey_",
    "appid",
    "apikey",
]


class SecretsLoader:
    """Loading and saving all requested secrets into connector folders"""

    logger: ClassVar[Logger] = Logger()
    if os.getenv("VERSION") == "dev":
        base_folder = Path(os.getcwd())
    else:
        base_folder = Path("/actions-runner/_work/airbyte/airbyte")

    def __init__(self, connector_name: str, gsm_credentials: Mapping[str, Any]):
        self.gsm_credentials = gsm_credentials
        self.connector_name = connector_name
        self._api = None

    @property
    def api(self) -> GoogleApi:
        if self._api is None:
            self._api = GoogleApi(self.gsm_credentials, GSM_SCOPES)
        return self._api

    def __load_gsm_secrets(self) -> Mapping[Tuple[str, str], str]:
        """Loads needed GSM secrets"""
        secrets = {}
        # docs: https://cloud.google.com/secret-manager/docs/filtering#api
        filter = "name:SECRET_"
        if self.connector_name:
            filter += f" AND labels.connector={self.connector_name}"
        url = f"https://secretmanager.googleapis.com/v1/projects/{self.api.project_id}/secrets"
        next_token = None
        while True:
            params = {
                "filter": filter,
            }
            if next_token:
                params["pageToken"] = next_token

            data = self.api.get(url, params=params)
            for secret_info in data.get("secrets") or []:
                secret_name = secret_info["name"]
                connector_name = secret_info.get("labels", {}).get("connector")
                if not connector_name:
                    self.logger.warning(f"secret {secret_name} doesn't have the label 'connector'")
                    continue
                elif self.connector_name and connector_name != self.connector_name:
                    self.logger.warning(f"incorrect the label connector '{connector_name}' of secret {secret_name}")
                    continue
                filename = secret_info.get("labels", {}).get("filename")
                if filename:
                    # all secret file names should be finished with ".json"
                    # but '.' cant be used in google, so we append it
                    filename = f"{filename}.json"
                else:
                    # the "filename" label is optional.
                    filename = DEFAULT_SECRET_FILE_WITH_EXT
                log_name = f'{secret_name.split("/")[-1]}({connector_name})'
                self.logger.info(f"found GSM secret: {log_name} = > {filename}")

                versions_url = f"https://secretmanager.googleapis.com/v1/{secret_name}/versions"
                data = self.api.get(versions_url)
                enabled_versions = [version["name"] for version in data["versions"] if version["state"] == "ENABLED"]
                if len(enabled_versions) > 1:
                    self.logger.critical(f"{log_name} should have one enabled version at the same time!!!")

                secret_url = f"https://secretmanager.googleapis.com/v1/{enabled_versions[0]}:access"
                data = self.api.get(secret_url)
                secret_value = data.get("payload", {}).get("data")
                if not secret_value:
                    self.logger.warning(f"{log_name} has empty value")
                    continue
                secret_value = base64.b64decode(secret_value.encode()).decode("utf-8")
                try:
                    # minimize and validate its JSON value
                    json_value = json.loads(secret_value)
                    secret_value = json.dumps(json_value, separators=(",", ":"))
                    self.mask_secrets_from_action_log(None, json_value)
                except JSONDecodeError as err:
                    self.logger.error(f"{log_name} has non-JSON value!!! Error: {err}")
                    continue
                secrets[(connector_name, filename)] = secret_value

            next_token = data.get("nextPageToken")
            if not next_token:
                break

        return secrets

    def mask_secrets_from_action_log(self, key, value):
        # recursive masking of json based on leaf key
        if not value:
            return
        elif isinstance(value, dict):
            for child, item in value.items():
                self.mask_secrets_from_action_log(child, item)
        elif isinstance(value, list):
            for item in value:
                self.mask_secrets_from_action_log(key, item)
        else:
            if key:
                # regular value, check for what to mask
                for pattern in MASK_KEY_PATTERNS:
                    if re.search(pattern, key):
                        self.logger.info(f"Add mask for key: {key}")
                        for line in str(value).splitlines():
                            line = str(line).strip()
                            # don't output } and such
                            if len(line) > 1 and not os.getenv("VERSION") == "dev":
                                # has to be at the beginning of line for Github to notice it
                                print(f"::add-mask::{line}")
                        break
            # see if it's really embedded json and get those values too
            try:
                json_value = json.loads(value)
                self.mask_secrets_from_action_log(None, json_value)
            except Exception:
                # carry on
                pass

    @staticmethod
    def generate_secret_name(connector_name: str, filename: str) -> str:
        """
        Generates an unique GSM secret name.
        Format of secret name: SECRET_<CAPITAL_CONNECTOR_NAME>_<OPTIONAL_UNIQUE_FILENAME_PART>__CREDS
        Examples:
            1. connector_name: source-linnworks, filename: dsdssds_a-b---_---_config.json
               => SECRET_SOURCE-LINNWORKS_DSDSSDS_A-B__CREDS
            2. connector_name: source-s3, filename: config.json
               => SECRET_SOURCE-LINNWORKS__CREDS
        """
        name_parts = ["secret", connector_name]
        filename_wo_ext = filename.replace(".json", "")
        if filename_wo_ext != DEFAULT_SECRET_FILE:
            name_parts.append(filename_wo_ext.replace(DEFAULT_SECRET_FILE, "").strip("_-"))
        name_parts.append("_creds")
        return "_".join(name_parts).upper()

    def create_secret(self, connector_name: str, filename: str, secret_value: str) -> bool:
        """
        Creates a new GSM secret with auto-generated name.
        """
        secret_name = self.generate_secret_name(connector_name, filename)
        self.logger.info(f"Generated the new secret name '{secret_name}' for {connector_name}({filename})")
        params = {
            "secretId": secret_name,
        }
        labels = {
            "connector": connector_name,
        }
        if filename != DEFAULT_SECRET_FILE:
            labels["filename"] = filename.replace(".json", "")
        body = {
            "labels": labels,
            "replication": {"automatic": {}},
        }
        url = f"https://secretmanager.googleapis.com/v1/projects/{self.api.project_id}/secrets"
        data = self.api.post(url, json=body, params=params)

        # try to create a new version
        secret_name = data["name"]
        self.logger.info(f"the GSM secret {secret_name} was created")
        secret_url = f"https://secretmanager.googleapis.com/v1/{secret_name}:addVersion"
        body = {"payload": {"data": base64.b64encode(secret_value.encode()).decode("utf-8")}}
        self.api.post(secret_url, json=body)
        return True

    def read_from_gsm(self) -> int:
        """Reads all necessary secrets from different sources"""
        secrets = self.__load_gsm_secrets()

        for k in secrets:
            if not isinstance(secrets[k], tuple):
                secrets[k] = ("GSM", secrets[k])
            source, _ = secrets[k]
            self.logger.info(f"Register the file {k[1]}({k[0]}) from {source}")

        if not len(secrets):
            self.logger.warning(f"not found any secrets of the connector '{self.connector_name}'")
            return {}
        return {k: v[1] for k, v in secrets.items()}

    def write_to_storage(self, secrets: Mapping[Tuple[str, str], str]) -> int:
        """Tries to save target secrets to the airbyte-integrations/connectors|bases/{connector_name}/secrets folder"""
        if not secrets:
            return 0
        for (connector_name, filename), secret_value in secrets.items():
            if connector_name == "base-normalization":
                secrets_dir = f"airbyte-integrations/bases/{connector_name}/secrets"
            else:
                secrets_dir = f"airbyte-integrations/connectors/{connector_name}/secrets"

            secrets_dir = self.base_folder / secrets_dir
            secrets_dir.mkdir(parents=True, exist_ok=True)
            filepath = secrets_dir / filename
            with open(filepath, "w") as file:
                file.write(secret_value)
            self.logger.info(f"The file {filepath} was saved")
        return 0

#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import json
import os
import re
from glob import glob
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, ClassVar, List, Mapping

import requests
import yaml

from .google_api import GoogleApi
from .logger import Logger
from .models import DEFAULT_SECRET_FILE, RemoteSecret, Secret


DEFAULT_SECRET_FILE_WITH_EXT = DEFAULT_SECRET_FILE + ".json"

GSM_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)

DEFAULT_MASK_KEY_PATTERNS = [
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
    "api_key",
]


class SecretsManager:
    """Loading, saving and updating all requested secrets into connector folders"""

    SPEC_MASK_URL = "https://connectors.airbyte.com/files/registries/v0/specs_secrets_mask.yaml"

    logger: ClassVar[Logger] = Logger()
    if os.getenv("VERSION") in ["dev", "dagger_ci"]:
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

    @property
    def mask_key_patterns(self) -> List[str]:
        return self._get_spec_mask() + DEFAULT_MASK_KEY_PATTERNS

    def __load_gsm_secrets(self) -> List[RemoteSecret]:
        """Loads needed GSM secrets"""
        secrets = []
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

            all_secrets_data = self.api.get(url, params=params)
            for secret_info in all_secrets_data.get("secrets") or []:
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
                versions_data = self.api.get(versions_url)
                enabled_versions = [version["name"] for version in versions_data["versions"] if version["state"] == "ENABLED"]
                if len(enabled_versions) > 1:
                    self.logger.critical(f"{log_name} should have one enabled version at the same time!!!")
                if not enabled_versions:
                    self.logger.warning(f"{log_name} doesn't have enabled versions for {secret_name}")
                    continue
                enabled_version = enabled_versions[0]
                secret_url = f"https://secretmanager.googleapis.com/v1/{enabled_version}:access"
                secret_data = self.api.get(secret_url)
                secret_value = secret_data.get("payload", {}).get("data")
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
                remote_secret = RemoteSecret(connector_name, filename, secret_value, enabled_version)
                secrets.append(remote_secret)

            next_token = all_secrets_data.get("nextPageToken")
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
                for pattern in self.mask_key_patterns:
                    if re.search(pattern, key):
                        self.logger.info(f"Add mask for key: {key}")
                        for line in str(value).splitlines():
                            line = str(line).strip()
                            # don't output } and such
                            if len(line) > 1:
                                if not os.getenv("VERSION") in ["dev", "dagger_ci"]:
                                    # has to be at the beginning of line for Github to notice it
                                    print(f"::add-mask::{line}")
                                if os.getenv("VERSION") == "dagger_ci":
                                    with open("/tmp/secrets_to_mask.txt", "a") as f:
                                        f.write(f"{line}\n")
                        break
            # see if it's really embedded json and get those values too
            try:
                json_value = json.loads(value)
                self.mask_secrets_from_action_log(None, json_value)
            except Exception:
                # carry on
                pass

    def read_from_gsm(self) -> List[RemoteSecret]:
        """Reads all necessary secrets from different sources"""
        secrets = self.__load_gsm_secrets()
        if not len(secrets):
            self.logger.warning(f"not found any secrets of the connector '{self.connector_name}'")
            return []
        return secrets

    def write_to_storage(self, secrets: List[RemoteSecret]) -> List[Path]:
        """Save target secrets to the airbyte-integrations/connectors|bases/{connector_name}/secrets folder

        Args:
            secrets (List[RemoteSecret]): List of remote secret to write locally

        Returns:
            List[Path]: List of paths were the secrets were written
        """
        written_files = []
        for secret in secrets:
            secrets_dir = self.base_folder / secret.directory
            secrets_dir.mkdir(parents=True, exist_ok=True)
            filepath = secrets_dir / secret.configuration_file_name
            with open(filepath, "w") as file:
                file.write(secret.value)
            written_files.append(filepath)
        return written_files

    def _create_new_secret_version(self, new_secret: Secret, old_secret: RemoteSecret) -> RemoteSecret:
        """Create a new secret version from a new secret instance. Disable the previous secret version.

        Args:
            new_secret (Secret): The new secret instance
            old_secret (RemoteSecret): The old secret instance

        Returns:
            RemoteSecret: The newly created remote secret instance
        """
        secret_url = f"https://secretmanager.googleapis.com/v1/projects/{self.api.project_id}/secrets/{new_secret.name}:addVersion"
        body = {"payload": {"data": base64.b64encode(new_secret.value.encode()).decode("utf-8")}}
        new_version_response = self.api.post(secret_url, json=body)
        self._disable_version(old_secret.enabled_version)
        return RemoteSecret.from_secret(new_secret, enabled_version=new_version_response["name"])

    def _disable_version(self, version_name: str) -> dict:
        """Disable a GSM secret version

        Args:
            version_name (str): Full name of the version (containing project id and secret name)

        Returns:
            dict: API response
        """
        disable_version_url = f"https://secretmanager.googleapis.com/v1/{version_name}:disable"
        return self.api.post(disable_version_url)

    def _get_updated_secrets(self) -> List[Secret]:
        """Find locally updated configurations files and return the most recent instance for each configuration file name.

        Returns:
            List[Secret]: List of Secret instances parsed from local updated configuration files
        """
        updated_configurations_glob = (
            f"{str(self.base_folder)}/airbyte-integrations/connectors/{self.connector_name}/secrets/updated_configurations/*.json"
        )
        updated_configuration_files_versions = {}
        for updated_configuration_path in glob(updated_configurations_glob):
            updated_configuration_path = Path(updated_configuration_path)
            with open(updated_configuration_path, "r") as updated_configuration:
                updated_configuration_value = json.load(updated_configuration)
            configuration_original_file_name = f"{updated_configuration_path.stem.split('|')[0]}{updated_configuration_path.suffix}"
            updated_configuration_files_versions.setdefault(configuration_original_file_name, [])
            updated_configuration_files_versions[configuration_original_file_name].append(
                (updated_configuration_value, os.path.getctime(str(updated_configuration_path)))
            )

        for updated_configurations in updated_configuration_files_versions.values():
            updated_configurations.sort(key=lambda x: x[1])
        return [
            Secret(
                connector_name=self.connector_name,
                configuration_file_name=configuration_file_name,
                value=json.dumps(versions_by_creation_time[-1][0]),
            )
            for configuration_file_name, versions_by_creation_time in updated_configuration_files_versions.items()
        ]

    def update_secrets(self, existing_secrets: List[RemoteSecret]) -> List[RemoteSecret]:
        """Update existing secrets if an updated version was found locally.

        Args:
            existing_secrets (List[RemoteSecret]): List of existing secrets for the current connector on GSM.

        Returns:
            List[RemoteSecret]: List of updated secrets as RemoteSecret instances
        """
        existing_secrets = {secret.name: secret for secret in existing_secrets}
        updated_secrets = {secret.name: secret for secret in self._get_updated_secrets()}
        new_remote_secrets = []
        for existing_secret_name in existing_secrets:
            if existing_secret_name in updated_secrets and json.loads(updated_secrets[existing_secret_name].value) != json.loads(
                existing_secrets[existing_secret_name].value
            ):
                new_secret = updated_secrets[existing_secret_name]
                old_secret = existing_secrets[existing_secret_name]
                new_remote_secret = self._create_new_secret_version(new_secret, old_secret)
                new_remote_secrets.append(new_remote_secret)
                self.logger.info(f"Updated {new_remote_secret.name} with new value")
        return new_remote_secrets

    def _get_spec_mask(self) -> List[str]:
        response = requests.get(self.SPEC_MASK_URL, allow_redirects=True)
        if not response.ok:
            self.logger.error(f"Failed to fetch spec mask: {response.content}")
        try:
            return yaml.safe_load(response.content)["properties"]
        except Exception as e:
            self.logger.error(f"Failed to parse spec mask: {e}")
            return []

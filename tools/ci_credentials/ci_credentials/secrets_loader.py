import base64
import json
import re
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Mapping, Any, Tuple, ClassVar

from ci_common_utils import GoogleApi
from ci_common_utils import Logger

DEFAULT_SECRET_FILE = "config"
DEFAULT_SECRET_FILE_WITH_EXT = DEFAULT_SECRET_FILE + ".json"

GSM_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)


@dataclass
class SecretsLoader:
    """
    """
    logger: ClassVar[Logger] = Logger()
    base_folder: ClassVar[Path] = Path("/Users/pixel/Projects/Airbyte/repo/")

    gsm_credentials: Mapping[str, Any]
    github_secrets: Mapping[str, str]

    connector_name: str = None
    _api: GoogleApi = None

    @classmethod
    def get_github_registers_filepath(cls) -> Path:
        return cls.base_folder / "tools/bin/ci_credentials.sh"

    def __read_github_registers_file(self) -> Mapping[Tuple[str, str], str]:
        """
            This function is used as workaround  for migration script.
            And it should be remove after final migration
        """
        registers_filepath = self.get_github_registers_filepath()
        if not registers_filepath.exists():
            return self.logger.critical(f"not found {registers_filepath} with GitHub registers")

        result = {}
        with open(registers_filepath, "r") as file:
            for line in file:
                line = re.sub(r"\s+", " ", line).strip()
                if not line.startswith("read_secrets"):
                    continue
                parts = line.split(" ")
                if len(parts) not in [3, 4]:
                    self.logger.warning(f"incorrect register line: {line}")
                    continue
                elif len(parts) == 3:
                    parts.append(DEFAULT_SECRET_FILE_WITH_EXT)
                _, connector_name, env_name, config_file = parts
                if self.connector_name and self.connector_name != connector_name:
                    continue
                env_name = env_name.strip("\"")[1:]
                config_file = config_file.strip("\"")

                self.logger.info(f"found register GitHub value: {connector_name}({env_name}) => {config_file}")

                secret = self.github_secrets.get(env_name)
                if not secret:
                    self.logger.warning(
                        f"secret key {env_name} of the connector {connector_name} was registered "
                        f"but it is not present into GitHub")
                    continue

                result[(connector_name, config_file)] = secret
        return result

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
            data, err = self.api.get(url, params=params)
            if err:
                return self.logger.critical(f"Google list error: {err}")

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
                secret_url = f"https://secretmanager.googleapis.com/v1/{secret_name}/versions/latest:access"

                data, err = self.api.get(secret_url)
                if err:
                    return self.logger.critical(f"Google secret's error {secret_url} => {err}")
                secret_value = data.get("payload", {}).get("data")
                if not secret_value:
                    self.logger.warning(f"{log_name} has empty value")
                    continue
                secret_value = base64.b64decode(secret_value.encode()).decode('utf-8')
                try:
                    # minimize and validate its JSON value
                    secret_value = json.dumps(json.loads(secret_value), separators=(',', ':'))
                except JSONDecodeError as err:
                    self.logger.error(f"{log_name} has non-JSON value!!! Error: {err}")
                    continue
                secrets[(connector_name, filename)] = secret_value
            next_token = data.get("nextPageToken")
            if not next_token:
                break
        return secrets

    @classmethod
    def generate_secret_name(cls, connector_name: str, filename: str) -> str:
        """
           Generates an unique GSM secret name.
           Format of secret name: SECRET_<CAPITAL_CONNECTOR_NAME>_<OPTIONAL_UNIQUE_FILENAME_PART>_CREDS
           Examples:
               1. connector_name: source-linnworks, filename: dsdssds_a-b---_---_config.json
                  => SECRET_SOURCE-LINNWORKS_DSDSSDS_A-B_CREDS
               2. connector_name: source-s3, filename: config.json
                  => SECRET_SOURCE-LINNWORKS_CREDS
        """
        name_parts = ["secret", connector_name]
        filename_wo_ext = filename.replace(".json", "")
        if filename_wo_ext != DEFAULT_SECRET_FILE:
            name_parts.append(filename_wo_ext.replace(DEFAULT_SECRET_FILE, "").strip("_-"))
        name_parts.append("creds")
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
        data, err = self.api.post(url, json=body, params=params)
        if err:
            self.logger.error(f"Can't create the new secret: {secret_name}, error: {err}")
            return False

        # try to create a new version
        secret_name = data["name"]
        self.logger.info(f"the GSM secret {secret_name} was created")
        secret_url = f'https://secretmanager.googleapis.com/v1/{secret_name}:addVersion'
        body = {
            "payload": {"data": base64.b64encode(secret_value.encode()).decode("utf-8")}
        }
        _, err = self.api.post(secret_url, json=body)
        if err:
            self.logger.error(f"Can't add the new version: {secret_name}, error: {err}")
        return err is None

    def read(self) -> int:
        """Reads all necessary secrets from different sources"""
        github_map = self.__read_github_registers_file()
        secrets = self.__load_gsm_secrets()

        # migrate secrets to GSM
        for connector_name_and_file in github_map:
            if connector_name_and_file not in secrets:
                self.logger.info(f"secret for {connector_name_and_file} is saved into GitHub only. "
                                 "Let's try to move it to GSM")
                if not self.create_secret(*connector_name_and_file,
                                          secret_value=github_map[connector_name_and_file]):
                    return self.logger.critical(f"can't create a secret for {connector_name_and_file}")

        # print summary register info
        for k in github_map:
            if k not in secrets:
                secrets[k] = ("GitHub", github_map[k])
        for k in secrets:
            if not isinstance(secrets[k], tuple):
                secrets[k] = ("GSM", secrets[k])
            source, _ = secrets[k]
            self.logger.info(f"Register the file {k[1]}({k[0]}) from {source}")

        if not len(secrets):
            return self.logger.critical(f"not found any secrets of the connector '{self.connector_name}'")
        return {k: v[1] for k, v in secrets.items()}

    def write(self, secrets: Mapping[Tuple[str, str], str]) -> int:
        if not secrets:
            return 1
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

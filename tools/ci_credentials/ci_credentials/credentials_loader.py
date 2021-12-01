import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Any, Tuple, ClassVar

from ci_common_utils import GoogleApi
from ci_common_utils import Logger

GITHUB_REGISTERS_FILE = "bin/ci_credentials.sh"
DEFAULT_SECRET_FILE = "config.json"
GSM_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)


@dataclass
class CredentialsLoader:
    """
    """
    logger: ClassVar[Logger] = Logger()

    gsm_credentials: Mapping[str, Any]
    github_secrets: Mapping[str, str]
    connector_name: str = None
    _api: GoogleApi = None

    def __read_github_registers_file(self) -> Mapping[Tuple[str, str], str]:
        """
            This function is used as workaround  for migration script.
            And it should be remove after final migration
        """
        path = Path(__file__)
        while str(path) != "/" and not str(path.absolute()).endswith("tools"):
            path = path.parent

        path /= GITHUB_REGISTERS_FILE
        if not path.exists():
            self.logger.warning("not found")
            return {}
        result = {}
        with open(path, "r") as file:
            for line in file:
                line = re.sub(r"\s+", " ", line).strip()
                if not line.startswith("read_secrets"):
                    continue
                parts = line.split(" ")
                if len(parts) not in [3, 4]:
                    self.logger.warning(f"incorrect register line: {line}")
                    continue
                elif len(parts) == 3:
                    parts.append(DEFAULT_SECRET_FILE)
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
        data, err = self.api.get("ggggggggg")
        if err:
            return self.logger.critical(f"Google error: {err}")
        pass

    def read(self) -> int:
        github_map = self.__read_github_registers_file()
        gsm_map = self.__load_gsm_secrets()
        raise Exception(github_map)
        pass

    def write(self) -> int:
        return 1

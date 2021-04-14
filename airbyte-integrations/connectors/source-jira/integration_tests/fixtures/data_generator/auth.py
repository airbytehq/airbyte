import json
import pathlib

from requests.auth import HTTPBasicAuth


class AuthClient:
    base_config_path = "secrets/config.json"
    base_headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self):
        self.configs = None
        super(AuthClient, self).__init__()

    def _get_configs(self):
        if not self.configs:
            source_directory = pathlib.Path(__file__).resolve().parent.parent.parent.parent
            configs_path = source_directory.joinpath(self.base_config_path)
            with open(configs_path) as json_configs:
                self.configs = json.load(json_configs)
        return self.configs

    def get_auth(self):
        configs = self._get_configs()
        auth = HTTPBasicAuth(configs.get("email"), configs.get("api_token"))
        return auth

    def get_headers(self):
        headers = self.base_headers
        return headers

    def get_base_url(self):
        configs = self._get_configs()
        base_url = f'https://{configs.get("domain")}/rest/api/3/'
        return base_url

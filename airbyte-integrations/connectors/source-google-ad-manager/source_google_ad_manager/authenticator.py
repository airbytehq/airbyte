import json
from googleads import ad_manager
from googleads import oauth2
from googleads.errors import GoogleAdsValueError
from typing import Any, Iterator, List, Mapping, MutableMapping
from pathlib import Path


API_VERSION = 'v202208'


class GoogleAdManagerAuthenticator:
    """responsible for generating the google_ad_manager authenticator object
    """

    def __init__(self, config: MutableMapping[str, Any], application_name: str):
        service_key_path = self.generate_json_file_from_credentials(config)
        try:
            self.oauth2_client = oauth2.GoogleServiceAccountClient(service_key_path, oauth2.GetAPIScope('ad_manager'))
        except GoogleAdsValueError as e:
            raise Exception(f"Error: {e}")
        self.ad_manager_client = ad_manager.AdManagerClient(self.oauth2_client, application_name)

    def generate_json_file_from_credentials(self, credentials: MutableMapping[str, Any]) -> str:
        """generates a json file from the credentials
        """
        # @todo: check if this does not have any security issues
        service_key_path = Path('/tmp/service_key.json')
        with open(service_key_path, 'w') as f:
            json.dump(credentials, f)
        return service_key_path

    def generate_report_downloader(self) -> ad_manager.DataDownloader:
        report_downloader = self.ad_manager_client.GetDataDownloader(version='v202208')
        return report_downloader

    def get_networks(self) -> List[Mapping[str, Any]]:
        network_service = self.ad_manager_client.GetService('NetworkService')
        networks = network_service.getAllNetworks()
        return networks

    def set_network(self, network):
        """update the client by setting the network

        Args:
            network (_type_): _description_
        """
        self.ad_manager_client.network_code = network['networkCode']

    def get_client(self) -> ad_manager.AdManagerClient:
        return self.ad_manager_client

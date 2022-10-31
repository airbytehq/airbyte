import json
from googleads import ad_manager
from googleads import oauth2
from googleads.common import ProxyConfig
from googleads.errors import GoogleAdsValueError
from typing import Any, List, Mapping, MutableMapping
from google.oauth2.service_account import Credentials


API_VERSION = 'v202208'


class CustomServiceAccountClient(oauth2.GoogleServiceAccountClient):
    """this is a custom service account client that implement from dict file instead of file path

    Args:
        oauth2 (_type_): _description_

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    def __init__(self, credentials_dict: Mapping[str, str], scope: str, sub=None, proxy_config=None):
        try:
            credentials_dict["private_key"] = credentials_dict["private_key"].replace("\\n", "\n")
            self.creds = (Credentials.from_service_account_info(credentials_dict, scopes=[scope], subject=sub))
        except KeyError as exc:
            raise GoogleAdsValueError(f"make sure the credentials dictionary has the following keys: {exc.args[0]}")
        self.proxy_config = (proxy_config if proxy_config else ProxyConfig())
        self.Refresh()
    

class GoogleAdManagerAuthenticator:
    """responsible for generating the google_ad_manager authenticator object
    """

    def __init__(self, config: MutableMapping[str, Any], application_name: str):
        try:
            self.oauth2_client = CustomServiceAccountClient(config, oauth2.GetAPIScope('ad_manager'))
        except GoogleAdsValueError as e:
            raise Exception(f"Error: {e}")
        self.ad_manager_client = ad_manager.AdManagerClient(self.oauth2_client, application_name)

    def generate_report_downloader(self) -> ad_manager.DataDownloader:
        report_downloader = self.ad_manager_client.GetDataDownloader(version=API_VERSION)
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

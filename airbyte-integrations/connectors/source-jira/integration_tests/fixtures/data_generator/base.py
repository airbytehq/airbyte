from abc import ABC, abstractmethod

import requests

from .auth import AuthClient


class BaseStream(ABC):
    def __init__(self):
        self.auth_client = AuthClient()
        super(BaseStream, self).__init__()

    @property
    @abstractmethod
    def list_endpoint(self):
        """List api endpoint of the stream"""

    @property
    @abstractmethod
    def generate_endpoint(self):
        """List api endpoint of the stream"""

    def get_url(self, endpoint):
        base_url = self.auth_client.get_base_url()
        url = f'{base_url}{endpoint}'
        return url

    def make_request(self, method, url, data=None):
        auth = self.auth_client.get_auth()
        headers = self.auth_client.get_headers()
        response = requests.request(method, url, data=data, headers=headers, auth=auth)
        return response

    @abstractmethod
    def list(self):
        """Returns list of items"""

    @abstractmethod
    def generate(self):
        """Creates batch of items"""

from airbyte_cdk.sources.streams.http import HttpStream
from abc import ABC
from source_active_campaign.auth import TokenAuthenticator


class ProxyStream(HttpStream, ABC):
    def __init__(self, authenticator: TokenAuthenticator = None, proxy_url: str = None):
        super().__init__(authenticator=authenticator)
        if proxy_url:
            self._session.proxies = {
                "https": proxy_url,
            }

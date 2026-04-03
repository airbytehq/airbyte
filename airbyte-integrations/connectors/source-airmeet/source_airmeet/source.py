"""
Source implementation for Airmeet.
"""
import logging
from typing import Any, List, Mapping, Optional, Tuple
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models import SyncMode

logger = logging.getLogger("airbyte")


class AirmeetAuthenticator:
    """Custom authenticator for Airmeet API"""
    
    def __init__(self, access_key: str, secret_key: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self._token = None
        self._auth_endpoint = "https://api-gateway.airmeet.com/prod/auth"
    
    @property
    def token(self) -> str:
        """Get or refresh token"""
        if not self._token:
            self._refresh_token()
        return self._token
    
    def _refresh_token(self):
        """Get new token from Airmeet auth API"""
        headers = {
            "Content-Type": "application/json",
            "x-airmeet-access-key": self.access_key,
            "x-airmeet-secret-key": self.secret_key
        }
        
        try:
            response = requests.post(self._auth_endpoint, headers=headers, timeout=30)
            response.raise_for_status()
            auth_data = response.json()
            self._token = auth_data.get("token")
            if not self._token:
                raise ValueError("No token in auth response")
            logger.info("Successfully refreshed Airmeet token")
        except Exception as e:
            logger.error(f"Failed to authenticate: {str(e)}")
            raise


class AirmeetStream(HttpStream):
    """Base stream for Airmeet API"""
    
    url_base = "https://api-gateway.airmeet.com"  # Without /prod
    primary_key = "uid"
    
    def __init__(self, authenticator: AirmeetAuthenticator, **kwargs):
        super().__init__(**kwargs)
        self._authenticator = authenticator
    
    @property
    def url(self) -> str:
        """Full URL for the endpoint"""
        return "https://api-gateway.airmeet.com/prod/airmeets"
    
    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/prod/airmeets"  # Full path including /prod
    
    def request_headers(
        self, stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """Add auth and content-type headers"""
        return {
            "Content-Type": "application/json",
            "x-airmeet-access-token": self._authenticator.token
        }
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Pagination logic if needed"""
        return None
    
    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> List[dict]:
        """Parse API response"""
        data = response.json()
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        elif isinstance(data, list):
            return data
        return [data]


class Airmeets(AirmeetStream):
    """Stream for fetching Airmeets"""
    pass  # All logic is in the parent class


class SourceAirmeet(AbstractSource):
    """Source implementation for Airmeet"""
    
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """Check connection to Airmeet API"""
        try:
            auth = AirmeetAuthenticator(
                access_key=config["access_key"],
                secret_key=config["secret_key"]
            )
            
            # Test the connection by getting auth token
            auth._refresh_token()
            
            # Try to fetch airmeets
            headers = {
                "Content-Type": "application/json",
                "x-airmeet-access-token": auth.token
            }
            
            response = requests.get(
                "https://api-gateway.airmeet.com/prod/airmeets",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            return True, None
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """Return list of streams"""
        auth = AirmeetAuthenticator(
            access_key=config["access_key"],
            secret_key=config["secret_key"]
        )
        return [
            Airmeets(authenticator=auth),
        ]
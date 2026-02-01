
"""
Custom authenticator for Airmeet API
"""
import logging
import requests
from typing import Any, Mapping, Optional
from dataclasses import dataclass, InitVar
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.types import Config

logger = logging.getLogger("airbyte")


@dataclass
class AirmeetAuthenticator(DeclarativeAuthenticator):
    """
    Custom authenticator for Airmeet API that:
    1. Calls auth endpoint with access_key and secret_key in headers
    2. Gets token from response
    3. Uses that token as x-airmeet-access-token header for all API calls
    """
    
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    access_key: str = ""
    secret_key: str = ""
    _token: Optional[str] = None
    _auth_endpoint: str = "https://api-gateway.airmeet.com/prod/auth"
    
    def __post_init__(self, parameters: Mapping[str, Any]):
        self.access_key = self.access_key or self.config.get("access_key", "")
        self.secret_key = self.secret_key or self.config.get("secret_key", "")
        self._token = None
        self._parameters = parameters
    
    def _get_token(self) -> str:
        """
        Get authentication token from Airmeet API
        """
        if not self._token:
            logger.info("Fetching new Airmeet access token...")
            
            headers = {
                "Content-Type": "application/json",
                "x-airmeet-access-key": self.access_key,
                "x-airmeet-secret-key": self.secret_key
            }
            
            try:
                response = requests.post(
                    self._auth_endpoint,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                
                auth_data = response.json()
                self._token = auth_data.get("token")
                
                if not self._token:
                    raise ValueError("No token in authentication response")
                
                logger.info("Successfully obtained Airmeet access token")
                
                # Log communityId for reference (useful for debugging)
                community_id = auth_data.get("communityId")
                if community_id:
                    logger.info(f"Community ID: {community_id}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to authenticate with Airmeet: {str(e)}")
                raise
            except (KeyError, ValueError) as e:
                logger.error(f"Invalid authentication response: {str(e)}")
                raise
        
        return self._token
    
    @property
    def auth_header(self) -> str:
        """Return the header name for authentication"""
        return "x-airmeet-access-token"
    
    @property
    def token(self) -> str:
        """Return the token value (without Bearer prefix)"""
        return self._get_token()
    
    def get_auth_header(self) -> Mapping[str, str]:
        """Return the authentication headers"""
        return {self.auth_header: self.token}
    
    def __call__(self, request):
        """Apply authentication to the request"""
        request.headers.update(self.get_auth_header())
        return request
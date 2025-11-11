from typing import Any, List, Mapping, Tuple, Optional
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
import requests
import time


class AirmeetAuthenticator:
    """Custom authenticator for Airmeet API"""
    
    def __init__(self, access_key: str, secret_key: str, region: str = "api-gateway"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self._token = None
        self._token_expiry = 0
    
    def get_token(self) -> str:
        """Get access token, refreshing if needed"""
        # Token valid for 30 days, refresh if expired or about to expire
        if self._token and time.time() < self._token_expiry:
            return self._token
        
        # Get new token
        url = f"https://{self.region}.airmeet.com/prod/auth"
        headers = {
            "X-Airmeet-Access-Key": self.access_key,
            "X-Airmeet-Secret-Key": self.secret_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Airmeet returns token directly (not wrapped in 'data')
        self._token = data["token"]
        # Set expiry to 29 days from now (with 1 day buffer)
        self._token_expiry = time.time() + (29 * 24 * 60 * 60)
        
        return self._token


class AirmeetStream(HttpStream):
    """Base stream for Airmeet API"""
    
    primary_key = "uid"
    page_size = 50
    
    def __init__(self, authenticator: AirmeetAuthenticator, airmeet_id: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self._authenticator = authenticator
        self.airmeet_id = airmeet_id
        self.region = authenticator.region
    
    @property
    def url_base(self) -> str:
        return f"https://{self.region}.airmeet.com/prod/"
    
    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """Set authentication headers"""
        return {
            "X-Airmeet-Access-Token": self._authenticator.get_token(),
            "Content-Type": "application/json"
        }
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Handle pagination using cursors"""
        try:
            data = response.json()
            cursors = data.get("cursors", {})
            after = cursors.get("after")
            
            if after:
                return {"after": after}
        except Exception:
            pass
        
        return None
    
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """Set query parameters including pagination"""
        params = {"size": self.page_size}
        
        if next_page_token:
            params.update(next_page_token)
        
        return params
    
    def parse_response(self, response: requests.Response, **kwargs) -> List[Mapping]:
        """Parse the response"""
        data = response.json()
        
        # Handle different response formats
        if "data" in data:
            result = data["data"]
        elif "sessions" in data:
            result = data["sessions"]
        elif "participants" in data:
            result = data["participants"]
        elif "booths" in data:
            result = data["booths"]
        elif "tracks" in data:
            result = data["tracks"]
        elif "customFields" in data:
            result = data["customFields"]
        else:
            result = data
        
        # Ensure we return a list
        if isinstance(result, list):
            return result
        return [result] if result else []


class Airmeets(AirmeetStream):
    """Stream for fetching all Airmeets (events)"""
    
    primary_key = "uid"
    
    def path(self, **kwargs) -> str:
        return "airmeets"
    
    def parse_response(self, response: requests.Response, **kwargs) -> List[Mapping]:
        data = response.json()
        return data.get("data", [])


class Participants(AirmeetStream):
    """Stream for fetching event participants"""
    
    primary_key = "email"
    page_size = 1000
    
    def path(self, **kwargs) -> str:
        if not self.airmeet_id:
            raise ValueError("airmeet_id is required for Participants stream")
        return f"airmeet/{self.airmeet_id}/participants"
    
    def parse_response(self, response: requests.Response, **kwargs) -> List[Mapping]:
        data = response.json()
        return data.get("participants", [])


class Sessions(AirmeetStream):
    """Stream for fetching event sessions"""
    
    primary_key = "sessionid"
    
    def path(self, **kwargs) -> str:
        if not self.airmeet_id:
            raise ValueError("airmeet_id is required for Sessions stream")
        return f"airmeet/{self.airmeet_id}/sessions"
    
    def parse_response(self, response: requests.Response, **kwargs) -> List[Mapping]:
        data = response.json()
        return data.get("sessions", [])


class CustomFields(AirmeetStream):
    """Stream for fetching custom registration fields"""
    
    primary_key = "fieldId"
    
    def path(self, **kwargs) -> str:
        if not self.airmeet_id:
            raise ValueError("airmeet_id is required for CustomFields stream")
        return f"airmeet/{self.airmeet_id}/custom-fields"
    
    def parse_response(self, response: requests.Response, **kwargs) -> List[Mapping]:
        data = response.json()
        return data.get("customFields", [])


class EventAttendance(AirmeetStream):
    """Stream for fetching event attendance"""
    
    primary_key = "id"
    
    def path(self, **kwargs) -> str:
        if not self.airmeet_id:
            raise ValueError("airmeet_id is required for EventAttendance stream")
        return f"airmeet/{self.airmeet_id}/attendees"
    
    def parse_response(self, response: requests.Response, **kwargs) -> List[Mapping]:
        if response.status_code == 202:
            return []
        data = response.json()
        return data.get("data", [])


class Booths(AirmeetStream):
    """Stream for fetching event booths"""
    
    primary_key = "uid"
    
    def path(self, **kwargs) -> str:
        if not self.airmeet_id:
            raise ValueError("airmeet_id is required for Booths stream")
        return f"airmeet/{self.airmeet_id}/booths"
    
    def parse_response(self, response: requests.Response, **kwargs) -> List[Mapping]:
        data = response.json()
        return data.get("booths", [])


class PollResponses(AirmeetStream):
    """Stream for fetching poll responses"""
    
    primary_key = "user_id"
    
    def path(self, **kwargs) -> str:
        if not self.airmeet_id:
            raise ValueError("airmeet_id is required for PollResponses stream")
        return f"airmeet/{self.airmeet_id}/polls"
    
    def parse_response(self, response: requests.Response, **kwargs) -> List[Mapping]:
        data = response.json()
        return data.get("data", [])


class QuestionsAsked(AirmeetStream):
    """Stream for fetching questions asked"""
    
    primary_key = "user_id"
    
    def path(self, **kwargs) -> str:
        if not self.airmeet_id:
            raise ValueError("airmeet_id is required for QuestionsAsked stream")
        return f"airmeet/{self.airmeet_id}/questions"
    
    def parse_response(self, response: requests.Response, **kwargs) -> List[Mapping]:
        data = response.json()
        return data.get("data", [])


class EventTracks(AirmeetStream):
    """Stream for fetching event tracks"""
    
    primary_key = "uid"
    
    def path(self, **kwargs) -> str:
        if not self.airmeet_id:
            raise ValueError("airmeet_id is required for EventTracks stream")
        return f"airmeet/{self.airmeet_id}/tracks"
    
    def parse_response(self, response: requests.Response, **kwargs) -> List[Mapping]:
        data = response.json()
        return data.get("tracks", [])


class RegistrationUTM(AirmeetStream):
    """Stream for fetching registration UTM"""
    
    primary_key = "email"
    
    def path(self, **kwargs) -> str:
        if not self.airmeet_id:
            raise ValueError("airmeet_id is required for RegistrationUTM stream")
        return f"airmeet/{self.airmeet_id}/utms"
    
    def parse_response(self, response: requests.Response, **kwargs) -> List[Mapping]:
        if response.status_code == 202:
            return []
        data = response.json()
        return data.get("data", [])


class SourceAirmeet(AbstractSource):
    """Airbyte Source for Airmeet"""
    
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """Test the connection to Airmeet API"""
        try:
            access_key = config.get("access_key", "")
            secret_key = config.get("secret_key", "")
            region = config.get("region", "api-gateway")
            
            if not access_key or not secret_key:
                return False, "access_key and secret_key are required in config"
            
            # Test authentication
            authenticator = AirmeetAuthenticator(access_key, secret_key, region)
            token = authenticator.get_token()
            
            if not token:
                return False, "Failed to obtain access token"
            
            # Test API call
            headers = {
                "X-Airmeet-Access-Token": token,
                "Content-Type": "application/json"
            }
            response = requests.get(
                f"https://{region}.airmeet.com/prod/airmeets?size=1",
                headers=headers
            )
            
            if response.status_code == 200:
                return True, None
            else:
                return False, f"API test failed: {response.status_code} - {response.text}"
        
        except Exception as e:
            return False, f"Failed to connect: {str(e)}"
    
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """Return a list of streams"""
        access_key = config["access_key"]
        secret_key = config["secret_key"]
        region = config.get("region", "api-gateway")
        airmeet_id = config.get("airmeet_id")
        
        authenticator = AirmeetAuthenticator(access_key, secret_key, region)
        
        streams = [
            Airmeets(authenticator=authenticator),
        ]
        
        if airmeet_id:
            streams.extend([
                Participants(authenticator=authenticator, airmeet_id=airmeet_id),
                Sessions(authenticator=authenticator, airmeet_id=airmeet_id),
                CustomFields(authenticator=authenticator, airmeet_id=airmeet_id),
                EventAttendance(authenticator=authenticator, airmeet_id=airmeet_id),
                Booths(authenticator=authenticator, airmeet_id=airmeet_id),
                PollResponses(authenticator=authenticator, airmeet_id=airmeet_id),
                QuestionsAsked(authenticator=authenticator, airmeet_id=airmeet_id),
                EventTracks(authenticator=authenticator, airmeet_id=airmeet_id),
                RegistrationUTM(authenticator=authenticator, airmeet_id=airmeet_id),
            ])
        
        return streams
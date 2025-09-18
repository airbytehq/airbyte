# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


class MockAPIClient:
    def __init__(self, api_url: str, timeout: int = 30):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def test_connection(self) -> bool:
        """Test connection to MockAPI by fetching users"""
        try:
            response = self.session.get(f"{self.api_url}/users", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_users(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get users from MockAPI"""
        try:
            params = {}
            if limit:
                params["limit"] = limit

            response = self.session.get(f"{self.api_url}/users", params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            raise

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user in MockAPI"""
        try:
            response = self.session.post(f"{self.api_url}/users", json=user_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing user in MockAPI"""
        try:
            response = self.session.put(f"{self.api_url}/users/{user_id}", json=user_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise

    def delete_user(self, user_id: str) -> bool:
        """Delete a user from MockAPI"""
        try:
            response = self.session.delete(f"{self.api_url}/users/{user_id}", timeout=self.timeout)
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False

    def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal in MockAPI"""
        try:
            response = self.session.post(f"{self.api_url}/deals", json=deal_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create deal: {e}")
            raise

    def get_deals(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get deals from MockAPI"""
        try:
            params = {}
            if limit:
                params["limit"] = limit

            response = self.session.get(f"{self.api_url}/deals", params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get deals: {e}")
            raise

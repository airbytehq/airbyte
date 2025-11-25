from typing import Optional
from airbyte_cdk.test.mock_http import HttpRequest


class HarvestRequestBuilder:
    """
    Builder for creating HTTP requests for Harvest API endpoints.

    This builder helps create clean, reusable request definitions for tests
    instead of manually constructing HttpRequest objects each time.

    Example usage:
        request = (
            HarvestRequestBuilder.clients_endpoint("123456", "test_token")
            .with_per_page(50)
            .with_page(2)
            .build()
        )
    """

    BASE_URL = "https://api.harvestapp.com/v2"

    @classmethod
    def clients_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /clients endpoint."""
        return cls("clients", account_id, api_token)

    @classmethod
    def projects_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /projects endpoint."""
        return cls("projects", account_id, api_token)

    @classmethod
    def time_entries_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /time_entries endpoint."""
        return cls("time_entries", account_id, api_token)

    @classmethod
    def users_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /users endpoint."""
        return cls("users", account_id, api_token)

    @classmethod
    def tasks_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /tasks endpoint."""
        return cls("tasks", account_id, api_token)

    @classmethod
    def company_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /company endpoint."""
        return cls("company", account_id, api_token)

    def __init__(self, resource: str, account_id: str, api_token: str):
        """
        Initialize the request builder.

        Args:
            resource: The API resource (e.g., 'clients', 'projects')
            account_id: The Harvest account ID
            api_token: The API token for authentication
        """
        self._resource = resource
        self._account_id = account_id
        self._api_token = api_token
        self._per_page: Optional[int] = None
        self._page: Optional[int] = None
        self._updated_since: Optional[str] = None
        self._query_params: dict = {}

    def with_per_page(self, per_page: int) -> "HarvestRequestBuilder":
        """Set the per_page query parameter for pagination."""
        self._per_page = per_page
        return self

    def with_page(self, page: int) -> "HarvestRequestBuilder":
        """Set the page query parameter for pagination."""
        self._page = page
        return self

    def with_updated_since(self, updated_since: str) -> "HarvestRequestBuilder":
        """Set the updated_since query parameter for incremental syncs."""
        self._updated_since = updated_since
        return self

    def with_query_param(self, key: str, value: str) -> "HarvestRequestBuilder":
        """Add a custom query parameter."""
        self._query_params[key] = value
        return self

    def build(self) -> HttpRequest:
        """
        Build and return the HttpRequest object.

        Returns:
            HttpRequest configured with the URL, query params, and headers
        """
        query_params = dict(self._query_params)

        if self._per_page is not None:
            query_params["per_page"] = str(self._per_page)
        if self._page is not None:
            query_params["page"] = str(self._page)
        if self._updated_since is not None:
            query_params["updated_since"] = self._updated_since

        return HttpRequest(
            url=f"{self.BASE_URL}/{self._resource}",
            query_params=query_params if query_params else None,
            headers={
                "Harvest-Account-Id": self._account_id,
                "Authorization": f"Bearer {self._api_token}"
            }
        )
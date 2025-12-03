# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

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

    @classmethod
    def contacts_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /contacts endpoint."""
        return cls("contacts", account_id, api_token)

    @classmethod
    def estimates_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /estimates endpoint."""
        return cls("estimates", account_id, api_token)

    @classmethod
    def expenses_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /expenses endpoint."""
        return cls("expenses", account_id, api_token)

    @classmethod
    def invoices_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /invoices endpoint."""
        return cls("invoices", account_id, api_token)

    @classmethod
    def roles_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /roles endpoint."""
        return cls("roles", account_id, api_token)

    @classmethod
    def user_assignments_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /user_assignments endpoint."""
        return cls("user_assignments", account_id, api_token)

    @classmethod
    def task_assignments_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /task_assignments endpoint."""
        return cls("task_assignments", account_id, api_token)

    @classmethod
    def invoice_payments_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /invoice_payments endpoint."""
        return cls("invoice_payments", account_id, api_token)

    @classmethod
    def project_assignments_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /project_assignments endpoint."""
        return cls("project_assignments", account_id, api_token)

    @classmethod
    def billable_rates_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /billable_rates endpoint."""
        return cls("billable_rates", account_id, api_token)

    @classmethod
    def cost_rates_endpoint(cls, account_id: str, api_token: str, user_id: int) -> "HarvestRequestBuilder":
        """Create a request builder for the /users/{user_id}/cost_rates endpoint."""
        return cls(f"users/{user_id}/cost_rates", account_id, api_token)

    @classmethod
    def estimate_item_categories_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /estimate_item_categories endpoint."""
        return cls("estimate_item_categories", account_id, api_token)

    @classmethod
    def estimate_messages_endpoint(cls, account_id: str, api_token: str, estimate_id: int) -> "HarvestRequestBuilder":
        """Create a request builder for the /estimates/{estimate_id}/messages endpoint."""
        return cls(f"estimates/{estimate_id}/messages", account_id, api_token)

    @classmethod
    def expense_categories_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /expense_categories endpoint."""
        return cls("expense_categories", account_id, api_token)

    @classmethod
    def expenses_categories_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /reports/expenses/categories endpoint."""
        return cls("reports/expenses/categories", account_id, api_token)

    @classmethod
    def expenses_clients_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /reports/expenses/clients endpoint."""
        return cls("reports/expenses/clients", account_id, api_token)

    @classmethod
    def expenses_projects_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /reports/expenses/projects endpoint."""
        return cls("reports/expenses/projects", account_id, api_token)

    @classmethod
    def expenses_team_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /reports/expenses/team endpoint."""
        return cls("reports/expenses/team", account_id, api_token)

    @classmethod
    def invoice_item_categories_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /invoice_item_categories endpoint."""
        return cls("invoice_item_categories", account_id, api_token)

    @classmethod
    def invoice_messages_endpoint(cls, account_id: str, api_token: str, invoice_id: int) -> "HarvestRequestBuilder":
        """Create a request builder for the /invoices/{invoice_id}/messages endpoint."""
        return cls(f"invoices/{invoice_id}/messages", account_id, api_token)

    @classmethod
    def project_budget_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /reports/project_budget endpoint."""
        return cls("reports/project_budget", account_id, api_token)

    @classmethod
    def time_clients_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /reports/time/clients endpoint."""
        return cls("reports/time/clients", account_id, api_token)

    @classmethod
    def time_projects_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /reports/time/projects endpoint."""
        return cls("reports/time/projects", account_id, api_token)

    @classmethod
    def time_tasks_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /reports/time/tasks endpoint."""
        return cls("reports/time/tasks", account_id, api_token)

    @classmethod
    def time_team_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /reports/time/team endpoint."""
        return cls("reports/time/team", account_id, api_token)

    @classmethod
    def uninvoiced_endpoint(cls, account_id: str, api_token: str) -> "HarvestRequestBuilder":
        """Create a request builder for the /reports/uninvoiced endpoint."""
        return cls("reports/uninvoiced", account_id, api_token)

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

    def with_from_date(self, from_date: str) -> "HarvestRequestBuilder":
        """Set the from query parameter for report streams."""
        self._query_params["from"] = from_date
        return self

    def with_to_date(self, to_date: str) -> "HarvestRequestBuilder":
        """Set the to query parameter for report streams."""
        self._query_params["to"] = to_date
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
            headers={"Harvest-Account-Id": self._account_id, "Authorization": f"Bearer {self._api_token}"},
        )

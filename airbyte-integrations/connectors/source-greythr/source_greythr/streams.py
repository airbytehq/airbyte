from typing import Any, Iterable, Mapping, MutableMapping, Optional
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

class Employees(HttpStream):
    """
    EmployeesStream handles fetching paginated employee data from the Greythr API.
    """

    url_base = ""  # This will be set using the configuration in the Source class
    primary_key = "employeeId"  # Define a unique key for each record, assuming "employee_id" is unique

    def __init__(self, config: Mapping[str, Any], authenticator:HttpAuthenticator):
        super().__init__(authenticator=authenticator)
        #self.token = authenticator.get_auth_header()
        self.gtHost = config["gtHost"]
        self.page = 1
        self.size = 50

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Handle pagination based on 'hasNext' field in response.
        """
        pages_info = response.json().get("pages", {})
        if pages_info.get("hasNext"):
            self.page += 1
            return {"page": self.page, "size": pages_info.get("size", self.size)}  # Use 'size' from response if available
        return None

    def request_headers(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, str]:
        """
        Generate headers required for the API request, including the domain and access token.
        """
        headers = super().request_headers(stream_slice=stream_slice, **kwargs)
        #headers["x-greythr-domain"] = self.gtHost
        #headers["ACCESS-TOKEN"] = self.token
        return headers

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        """
        Set the path for the employees endpoint.
        """
        return "https://api.greythr.com/employee/v2/employees"

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        """
        Define request parameters, including pagination.
        """
        params = {
            "page": self.page,
            "size": self.size
        }
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse the response JSON and yield each employee record.
        """
        data = response.json().get("data", [])
        for record in data:
            yield record

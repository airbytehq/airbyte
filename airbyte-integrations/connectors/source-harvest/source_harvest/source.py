# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import pendulum
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models import SyncMode
from .auth import HarvestTokenAuthenticator

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""


class HarvestStream(HttpStream, ABC):
    url_base = "https://api.harvestapp.com/v2/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass


class HarvestStreamWithPagination(HarvestStream):
    per_page = 50
    primary_key = "id"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        if stream_data["next_page"] is not None:
            return {
                "page": stream_data["next_page"],
            }

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token=next_page_token, **kwargs)
        params["per_page"] = self.per_page
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        records = response.json()[self.data_field]
        for record in records:
            yield record


class HarvestStreamWithPaginationSliced(HarvestStreamWithPagination):
    @property
    @abstractmethod
    def parent_stream(self) -> str:
        """
        :return: parent stream class
        """

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        items = self.parent_stream(authenticator=self.authenticator)
        for item in items.read_records(sync_mode=kwargs.get("sync_mode", SyncMode.full_refresh)):
            yield {"parent_id": item["id"]}


class HarvestStreamNoPagition(HarvestStream):
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()


class Contacts(HarvestStreamWithPagination):
    data_field = "contacts"

    def path(self, **kwargs) -> str:
        return "contacts"


class Clients(HarvestStreamWithPagination):
    data_field = "clients"

    def path(self, **kwargs) -> str:
        return "clients"


class Company(HarvestStreamNoPagition):
    primary_key = None
    data_field = None

    def path(self, **kwargs) -> str:
        return "company"


class Invoices(HarvestStreamWithPagination):
    data_field = "invoices"

    def path(self, **kwargs) -> str:
        return "invoices"


class InvoiceMessages(HarvestStreamWithPaginationSliced):
    data_field = "invoice_messages"
    parent_stream = Invoices

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"invoices/{stream_slice['parent_id']}/messages"


class InvoicePayments(HarvestStreamWithPaginationSliced):
    data_field = "invoice_payments"
    parent_stream = Invoices

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"invoices/{stream_slice['parent_id']}/payments"


class InvoiceItemCategories(HarvestStreamWithPagination):
    data_field = "invoice_item_categories"

    def path(self, **kwargs) -> str:
        return "invoice_item_categories"


class Estimates(HarvestStreamWithPagination):
    data_field = "estimates"

    def path(self, **kwargs) -> str:
        return "estimates"


class EstimateMessages(HarvestStreamWithPaginationSliced):
    data_field = "estimates"
    parent_stream = Estimates

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"estimates/{stream_slice['parent_id']}/messages"


class EstimateItemCategories(HarvestStreamWithPagination):
    data_field = "estimate_item_categories"

    def path(self, **kwargs) -> str:
        return "estimate_item_categories"


class Expenses(HarvestStreamWithPagination):
    data_field = "expenses"

    def path(self, **kwargs) -> str:
        return "expenses"


class ExpenseCategories(HarvestStreamWithPagination):
    data_field = "expense_categories"

    def path(self, **kwargs) -> str:
        return "expense_categories"


class Tasks(HarvestStreamWithPagination):
    data_field = "tasks"

    def path(self, **kwargs) -> str:
        return "tasks"


class TimeEntries(HarvestStreamWithPagination):
    data_field = "time_entries"

    def path(self, **kwargs) -> str:
        return "time_entries"


class UserAssignments(HarvestStreamWithPagination):
    data_field = "user_assignments"

    def path(self, **kwargs) -> str:
        return "user_assignments"


class TaskAssignments(HarvestStreamWithPagination):
    data_field = "task_assignments"

    def path(self, **kwargs) -> str:
        return "task_assignments"

class Projects(HarvestStreamWithPagination):
    data_field = "projects"

    def path(self, **kwargs) -> str:
        return "projects"


class Roles(HarvestStreamWithPagination):
    data_field = "roles"

    def path(self, **kwargs) -> str:
        return "roles"


class Users(HarvestStreamWithPagination):
    data_field = "users"

    def path(self, **kwargs) -> str:
        return "users"


class BillableRates(HarvestStreamWithPaginationSliced):
    data_field = "billable_rates"
    parent_stream = Users

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"users/{stream_slice['parent_id']}/billable_rates"


class BillableRates(HarvestStreamWithPaginationSliced):
    data_field = "billable_rates"
    parent_stream = Users

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"users/{stream_slice['parent_id']}/billable_rates"


class CostRates(HarvestStreamWithPaginationSliced):
    data_field = "cost_rates"
    parent_stream = Users

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"users/{stream_slice['parent_id']}/cost_rates"


class ProjectAssignments(HarvestStreamWithPaginationSliced):
    data_field = "project_assignments"
    parent_stream = Users

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"users/{stream_slice['parent_id']}/project_assignments"


class ExpensesBase(HarvestStreamWithPagination):
    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        current_date = pendulum.now()
        # `from` and `to` params are required for expenses reports calls
        # min `from` value is current_date - 1 year
        params.update({
            "from": current_date.subtract(years=1).format("%Y%m%d"),
            "to": current_date
        })
        return params


class ExpensesClients(ExpensesBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/expenses/clients"


class ExpensesProjects(ExpensesBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/expenses/projects"


class ExpensesCategories(ExpensesBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/expenses/categories"


class ExpensesTeam(ExpensesBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/expenses/team"


class IncrementalHarvestStream(HarvestStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class Employees(IncrementalHarvestStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the cursor_field. Required.
    cursor_field = "start_date"

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "employee_id"

    def path(self, **kwargs) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
        return "single". Required.
        """
        return "employees"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        TODO: Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

        Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
        This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
        section of the docs for more information.

        The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
        necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
        This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

        An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
        craft that specific request.

        For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
        this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
        till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
        the date query param.
        """
        raise NotImplementedError("Implement stream slices or delete this method!")


class SourceHarvest(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = HarvestTokenAuthenticator(token=config["api_token"], account_id=config["account_id"])

        streams = [
            Clients(authenticator=auth),
            Contacts(authenticator=auth),
            Company(authenticator=auth),
            Invoices(authenticator=auth),
            InvoiceMessages(authenticator=auth),
            InvoicePayments(authenticator=auth),
            InvoiceItemCategories(authenticator=auth),
            Estimates(authenticator=auth),
            EstimateMessages(authenticator=auth),
            EstimateItemCategories(authenticator=auth),
            Expenses(authenticator=auth),
            ExpenseCategories(authenticator=auth),
            Tasks(authenticator=auth),
            TimeEntries(authenticator=auth),
            UserAssignments(authenticator=auth),
            TaskAssignments(authenticator=auth),
            Projects(authenticator=auth),
            Roles(authenticator=auth),
            Users(authenticator=auth),
            BillableRates(authenticator=auth),
            CostRates(authenticator=auth),
            ProjectAssignments(authenticator=auth),
            ExpensesClients(authenticator=auth),
            ExpensesProjects(authenticator=auth),
            ExpensesCategories(authenticator=auth),
            ExpensesTeam(authenticator=auth),
        ]

        return streams

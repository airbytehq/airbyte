#
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
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class HarvestStream(HttpStream, ABC):
    url_base = "https://api.harvestapp.com/v2/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass


class HarvestStreamWithPagination(HarvestStream):
    per_page = 50
    primary_key = "id"

    @property
    @abstractmethod
    def data_field(self) -> str:
        """
        :return: Default field name to get data from response
        """

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
    def parent_stream(self) -> HarvestStreamWithPagination:
        """
        :return: parent stream class
        """

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:
        updated_since = self._updated_since
        if stream_state and stream_state.get(self.cursor_field):
            updated_since = stream_state[self.cursor_field]
        items = self.parent_stream(authenticator=self.authenticator, updated_since=updated_since)
        for item in items.read_records(sync_mode=sync_mode):
            yield {"parent_id": item["id"]}


class HarvestStreamIncrementalMixin(HttpStream, ABC):
    cursor_field = "updated_at"

    def __init__(self, updated_since: pendulum.datetime, **kwargs):
        super().__init__(**kwargs)
        self._updated_since = updated_since

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state)
        updated_since = self._updated_since
        if stream_state.get(self.cursor_field):
            updated_since = stream_state[self.cursor_field]
        params.update({"updated_since": updated_since})
        return params


class Contacts(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "contacts"

    def path(self, **kwargs) -> str:
        return "contacts"


class Clients(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "clients"

    def path(self, **kwargs) -> str:
        return "clients"


class Company(HarvestStream):
    primary_key = None
    data_field = None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()

    def path(self, **kwargs) -> str:
        return "company"


class Invoices(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "invoices"

    def path(self, **kwargs) -> str:
        return "invoices"


class InvoiceMessages(HarvestStreamWithPaginationSliced, HarvestStreamIncrementalMixin):
    data_field = "invoice_messages"
    parent_stream = Invoices

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"invoices/{stream_slice['parent_id']}/messages"


class InvoicePayments(HarvestStreamWithPaginationSliced, HarvestStreamIncrementalMixin):
    data_field = "invoice_payments"
    parent_stream = Invoices

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"invoices/{stream_slice['parent_id']}/payments"


class InvoiceItemCategories(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "invoice_item_categories"

    def path(self, **kwargs) -> str:
        return "invoice_item_categories"


class Estimates(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "estimates"

    def path(self, **kwargs) -> str:
        return "estimates"


class EstimateMessages(HarvestStreamWithPaginationSliced, HarvestStreamIncrementalMixin):
    data_field = "estimate_messages"
    parent_stream = Estimates

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"estimates/{stream_slice['parent_id']}/messages"


class EstimateItemCategories(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "estimate_item_categories"

    def path(self, **kwargs) -> str:
        return "estimate_item_categories"


class Expenses(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "expenses"

    def path(self, **kwargs) -> str:
        return "expenses"


class ExpenseCategories(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "expense_categories"

    def path(self, **kwargs) -> str:
        return "expense_categories"


class Tasks(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "tasks"

    def path(self, **kwargs) -> str:
        return "tasks"


class TimeEntries(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "time_entries"

    def path(self, **kwargs) -> str:
        return "time_entries"


class UserAssignments(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "user_assignments"

    def path(self, **kwargs) -> str:
        return "user_assignments"


class TaskAssignments(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "task_assignments"

    def path(self, **kwargs) -> str:
        return "task_assignments"


class Projects(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "projects"

    def path(self, **kwargs) -> str:
        return "projects"


class Roles(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "roles"

    def path(self, **kwargs) -> str:
        return "roles"


class Users(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    data_field = "users"

    def path(self, **kwargs) -> str:
        return "users"


class BillableRates(HarvestStreamWithPaginationSliced, HarvestStreamIncrementalMixin):
    data_field = "billable_rates"
    parent_stream = Users

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"users/{stream_slice['parent_id']}/billable_rates"


class CostRates(HarvestStreamWithPaginationSliced, HarvestStreamIncrementalMixin):
    data_field = "cost_rates"
    parent_stream = Users

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"users/{stream_slice['parent_id']}/cost_rates"


class ProjectAssignments(HarvestStreamWithPaginationSliced, HarvestStreamIncrementalMixin):
    data_field = "project_assignments"
    parent_stream = Users

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"users/{stream_slice['parent_id']}/project_assignments"


class ReportsBase(HarvestStreamWithPagination, ABC):
    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        current_date = pendulum.now()
        # `from` and `to` params are required for expenses reports calls
        # min `from` value is current_date - 1 year
        params.update({"from": current_date.subtract(years=1).strftime("%Y%m%d"), "to": current_date.strftime("%Y%m%d")})
        return params


class ExpensesClients(ReportsBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/expenses/clients"


class ExpensesProjects(ReportsBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/expenses/projects"


class ExpensesCategories(ReportsBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/expenses/categories"


class ExpensesTeam(ReportsBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/expenses/team"


class Uninvoiced(ReportsBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/uninvoiced"


class TimeClients(ReportsBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/time/clients"


class TimeProjects(ReportsBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/time/projects"


class TimeTasks(ReportsBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/time/tasks"


class TimeTeam(ReportsBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/time/team"


class ProjectBudget(ReportsBase):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "reports/project_budget"

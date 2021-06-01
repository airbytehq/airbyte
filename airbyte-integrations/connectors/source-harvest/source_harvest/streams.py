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
    def data_field(self) -> str:
        """
        :return: Default field name to get data from response
        """
        return self.name

    def path(self, **kwargs) -> str:
        return self.name

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        if stream_data.get("next_page"):
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
        records = response.json().get(self.data_field, [])
        yield from records


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
        params = super().request_params(stream_state=stream_state, **kwargs)
        updated_since = pendulum.parse(self._updated_since)
        if stream_state.get(self.cursor_field):
            updated_since = stream_state[self.cursor_field]
        params.update({"updated_since": updated_since})
        return params


class HarvestStreamWithPaginationSliced(HarvestStreamWithPagination):
    @property
    @abstractmethod
    def parent_stream_name(self) -> str:
        """
        :return: parent stream class name
        """

    def stream_slices(self, sync_mode: SyncMode, cursor_field: List[str] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        parent_stream = type(self.parent_stream_name, (HarvestStreamWithPagination,), {})
        items = parent_stream(authenticator=self.authenticator)
        for item in items.read_records(sync_mode=sync_mode):
            yield {"parent_id": item["id"]}


class Contacts(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class Clients(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class Company(HarvestStream):
    primary_key = None
    data_field = None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()

    def path(self, **kwargs) -> str:
        return self.name


class Invoices(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class InvoiceMessages(HarvestStreamWithPaginationSliced, HarvestStreamIncrementalMixin):
    parent_stream_name = "Invoices"

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"invoices/{stream_slice['parent_id']}/messages"


class InvoicePayments(HarvestStreamWithPaginationSliced, HarvestStreamIncrementalMixin):
    parent_stream_name = "Invoices"

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"invoices/{stream_slice['parent_id']}/payments"


class InvoiceItemCategories(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class Estimates(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class EstimateMessages(HarvestStreamWithPaginationSliced, HarvestStreamIncrementalMixin):
    parent_stream_name = "Estimates"

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"estimates/{stream_slice['parent_id']}/messages"


class EstimateItemCategories(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class Expenses(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class ExpenseCategories(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class Tasks(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class TimeEntries(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class UserAssignments(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class TaskAssignments(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class Projects(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class Roles(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    pass


class Users(HarvestStreamWithPagination, HarvestStreamIncrementalMixin):
    def path(self, **kwargs) -> str:
        return self.name


class BillableRates(HarvestStreamWithPaginationSliced):
    parent_stream_name = "Users"

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"users/{stream_slice['parent_id']}/billable_rates"


class CostRates(HarvestStreamWithPaginationSliced):
    parent_stream_name = "Users"

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"users/{stream_slice['parent_id']}/cost_rates"


class ProjectAssignments(HarvestStreamWithPaginationSliced, HarvestStreamIncrementalMixin):
    parent_stream_name = "Users"

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"users/{stream_slice['parent_id']}/project_assignments"


class ReportsBase(HarvestStreamWithPagination, ABC):
    data_field = "results"
    date_param_template = "%Y%m%d"

    def __init__(self, from_date: pendulum.date = pendulum.now().date().subtract(years=1), **kwargs):
        super().__init__(**kwargs)
        self._from_date = from_date

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        current_date = pendulum.now()
        # `from` and `to` params are required for expenses reports calls
        # min `from` value is current_date - 1 year
        params.update({"from": self._from_date.strftime("%Y%m%d"), "to": current_date.strftime("%Y%m%d")})
        return params


class ExpensesClients(ReportsBase):
    def path(self, **kwargs) -> str:
        return "reports/expenses/clients"


class ExpensesProjects(ReportsBase):
    def path(self, **kwargs) -> str:
        return "reports/expenses/projects"


class ExpensesCategories(ReportsBase):
    def path(self, **kwargs) -> str:
        return "reports/expenses/categories"


class ExpensesTeam(ReportsBase):
    def path(self, **kwargs) -> str:
        return "reports/expenses/team"


class Uninvoiced(ReportsBase):
    def path(self, **kwargs) -> str:
        return "reports/uninvoiced"


class TimeClients(ReportsBase):
    def path(self, **kwargs) -> str:
        return "reports/time/clients"


class TimeProjects(ReportsBase):
    def path(self, **kwargs) -> str:
        return "reports/time/projects"


class TimeTasks(ReportsBase):
    def path(self, **kwargs) -> str:
        return "reports/time/tasks"


class TimeTeam(ReportsBase):
    def path(self, **kwargs) -> str:
        return "reports/time/team"


class ProjectBudget(ReportsBase):
    def path(self, **kwargs) -> str:
        return "reports/project_budget"

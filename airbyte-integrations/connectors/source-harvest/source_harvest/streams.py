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

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["per_page"] = self.per_page
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        stream_data = response.json()

        # depending on stream type we may get either:
        # * nested records iterable in response object;
        # * not nested records iterable;
        # * single object to yield.
        if self.data_field:
            stream_data = response.json().get(self.data_field, [])

        if isinstance(stream_data, list):
            yield from stream_data
        else:
            yield stream_data


class IncrementalHarvestStream(HarvestStream, ABC):
    cursor_field = "updated_at"

    def __init__(self, updated_since: pendulum.datetime = None, **kwargs):
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

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        updated_since = stream_state.get(self.cursor_field) or self._updated_since
        params.update({"updated_since": updated_since})
        return params


class HarvestSubStream(HarvestStream):
    @property
    @abstractmethod
    def path_template(self) -> str:
        """
        :return: sub stream path template
        """

    @property
    @abstractmethod
    def parent_stream(self) -> IncrementalHarvestStream:
        """
        :return: parent stream class
        """

    def stream_slices(self, sync_mode: SyncMode, cursor_field: List[str] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        items = self.parent_stream(authenticator=self.authenticator)
        for item in items.read_records(sync_mode=sync_mode):
            yield {"parent_id": item["id"]}

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return self.path_template.format(parent_id=stream_slice["parent_id"])


class Contacts(IncrementalHarvestStream):
    pass


class Clients(IncrementalHarvestStream):
    pass


class Company(HarvestStream):
    primary_key = None
    data_field = None


class Invoices(IncrementalHarvestStream):
    pass


class InvoiceMessages(HarvestSubStream, IncrementalHarvestStream):
    parent_stream = Invoices
    path_template = "invoices/{parent_id}/messages"


class InvoicePayments(HarvestSubStream, IncrementalHarvestStream):
    parent_stream = Invoices
    path_template = "invoices/{parent_id}/payments"


class InvoiceItemCategories(IncrementalHarvestStream):
    pass


class Estimates(IncrementalHarvestStream):
    pass


class EstimateMessages(HarvestSubStream, IncrementalHarvestStream):
    parent_stream = Estimates
    path_template = "estimates/{parent_id}/messages"


class EstimateItemCategories(IncrementalHarvestStream):
    pass


class Expenses(IncrementalHarvestStream):
    pass


class ExpenseCategories(IncrementalHarvestStream):
    pass


class Tasks(IncrementalHarvestStream):
    pass


class TimeEntries(IncrementalHarvestStream):
    pass


class UserAssignments(IncrementalHarvestStream):
    pass


class TaskAssignments(IncrementalHarvestStream):
    pass


class Projects(IncrementalHarvestStream):
    pass


class Roles(IncrementalHarvestStream):
    pass


class Users(IncrementalHarvestStream):
    pass


class BillableRates(HarvestSubStream):
    parent_stream = Users
    path_template = "users/{parent_id}/billable_rates"


class CostRates(HarvestSubStream):
    parent_stream = Users
    path_template = "users/{parent_id}/cost_rates"


class ProjectAssignments(HarvestSubStream, IncrementalHarvestStream):
    parent_stream = Users
    path_template = "users/{parent_id}/project_assignments"


class ReportsBase(HarvestStream, ABC):
    data_field = "results"
    date_param_template = "%Y%m%d"

    @property
    @abstractmethod
    def report_path(self):
        """
        :return: report path suffix
        """

    def __init__(self, from_date: pendulum.date = None, **kwargs):
        super().__init__(**kwargs)
        self._from_date = from_date or pendulum.now().date().subtract(years=1)

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        current_date = pendulum.now()
        # `from` and `to` params are required for reports calls
        # min `from` value is current_date - 1 year
        params.update({"from": self._from_date.strftime("%Y%m%d"), "to": current_date.strftime("%Y%m%d")})
        return params

    def path(self, **kwargs) -> str:
        return f"reports/{self.report_path}"


class ExpensesClients(ReportsBase):
    report_path = "expenses/clients"


class ExpensesProjects(ReportsBase):
    report_path = "expenses/projects"


class ExpensesCategories(ReportsBase):
    report_path = "expenses/categories"


class ExpensesTeam(ReportsBase):
    report_path = "expenses/team"


class Uninvoiced(ReportsBase):
    report_path = "uninvoiced"


class TimeClients(ReportsBase):
    report_path = "time/clients"


class TimeProjects(ReportsBase):
    report_path = "time/projects"


class TimeTasks(ReportsBase):
    report_path = "time/tasks"


class TimeTeam(ReportsBase):
    report_path = "time/team"


class ProjectBudget(ReportsBase):
    report_path = "project_budget"

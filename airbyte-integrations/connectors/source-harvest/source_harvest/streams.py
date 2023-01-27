#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import parse_qsl, urlparse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream


class HarvestStream(HttpStream, ABC):
    url_base = "https://api.harvestapp.com/v2/"
    per_page = 50
    primary_key = "id"
    raise_on_http_errors = True

    @property
    def data_field(self) -> str:
        """
        :return: Default field name to get data from response
        """
        return self.name

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def backoff_time(self, response: requests.Response):
        if "Retry-After" in response.headers:
            return int(response.headers["Retry-After"])
        else:
            self.logger.info("Retry-after header not found. Using default backoff value")
            return super().backoff_time(response)

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

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == requests.codes.FORBIDDEN:
            setattr(self, "raise_on_http_errors", False)
            self.logger.warn(f"Stream `{self.name}` is not available. Please check required permissions. {response.text}")
        return super().should_retry(response)


class IncrementalHarvestStream(HarvestStream, ABC):
    cursor_field = "updated_at"

    def __init__(self, replication_start_date: pendulum.datetime = None, **kwargs):
        super().__init__(**kwargs)
        self._replication_start_date = replication_start_date

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
        replication_start_date = stream_state.get(self.cursor_field) or self._replication_start_date
        params.update({"updated_since": replication_start_date})
        return params


class HarvestSubStream(HarvestStream, ABC):
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

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        items = self.parent_stream(authenticator=self.authenticator)
        for item in items.read_records(sync_mode=SyncMode.full_refresh):
            yield {"parent_id": item["id"]}

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return self.path_template.format(parent_id=stream_slice["parent_id"])

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, stream_slice=stream_slice, **kwargs):
            record["parent_id"] = stream_slice["parent_id"]
            yield record


class Contacts(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/clients-api/clients/contacts/
    """


class Clients(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/clients-api/clients/clients/
    """


class Company(HarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/company-api/company/company/
    """

    primary_key = None
    data_field = None


class Invoices(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/invoices-api/invoices/invoices/
    """


class InvoiceMessages(HarvestSubStream, IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/invoices-api/invoices/invoice-messages/
    """

    parent_stream = Invoices
    path_template = "invoices/{parent_id}/messages"


class InvoicePayments(HarvestSubStream, IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/invoices-api/invoices/invoice-payments/
    """

    parent_stream = Invoices
    path_template = "invoices/{parent_id}/payments"


class InvoiceItemCategories(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/invoices-api/invoices/invoice-item-categories/
    """


class Estimates(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/estimates-api/estimates/estimates/
    """


class EstimateMessages(HarvestSubStream, IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/estimates-api/estimates/estimate-messages/
    """

    parent_stream = Estimates
    path_template = "estimates/{parent_id}/messages"


class EstimateItemCategories(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/estimates-api/estimates/estimate-item-categories/
    """


class Expenses(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/expenses-api/expenses/expenses/
    """


class ExpenseCategories(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/expenses-api/expenses/expense-categories/
    """


class Tasks(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/tasks-api/tasks/tasks/
    """


class TimeEntries(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/timesheets-api/timesheets/time-entries/
    """


class UserAssignments(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/projects-api/projects/user-assignments/
    """


class TaskAssignments(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/projects-api/projects/task-assignments/
    """


class Projects(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/projects-api/projects/projects/
    """


class Roles(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/roles-api/roles/roles/
    """


class Users(IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/users-api/users/users/
    """


class BillableRates(HarvestSubStream):
    """
    Docs: https://help.getharvest.com/api-v2/users-api/users/billable-rates/
    """

    parent_stream = Users
    path_template = "users/{parent_id}/billable_rates"


class CostRates(HarvestSubStream):
    """
    Docs: https://help.getharvest.com/api-v2/users-api/users/cost-rates/
    """

    parent_stream = Users
    path_template = "users/{parent_id}/cost_rates"


class ProjectAssignments(HarvestSubStream, IncrementalHarvestStream):
    """
    Docs: https://help.getharvest.com/api-v2/users-api/users/project-assignments/
    """

    parent_stream = Users
    path_template = "users/{parent_id}/project_assignments"


class ReportsBase(HarvestStream, ABC):
    data_field = "results"
    date_param_template = "%Y%m%d"
    primary_key = None

    @property
    @abstractmethod
    def report_path(self):
        """
        :return: report path suffix
        """

    def __init__(self, from_date: Optional[pendulum.date] = None, to_date: Optional[pendulum.date] = None, **kwargs):
        super().__init__(**kwargs)

        current_date = pendulum.now().date()
        self._from_date = from_date or current_date.subtract(years=1)
        self._to_date = to_date or current_date
        # `to` date greater than `from` date causes an exception on Harvest
        if self._from_date > current_date:
            self._to_date = from_date

    def path(self, **kwargs) -> str:
        return f"reports/{self.report_path}"


class IncrementalReportsBase(ReportsBase, ABC):
    cursor_field = "to"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        parsed_url = urlparse(response.url)
        params = dict(parse_qsl(parsed_url.query))

        records = response.json().get(self.data_field, [])
        for record in records:
            record.update(
                {
                    "from": params.get("from", self._from_date.strftime(self.date_param_template)),
                    "to": params.get("to", self._to_date.strftime(self.date_param_template)),
                }
            )
            yield record

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, **kwargs)
        params = {**params, **stream_slice} if stream_slice else params
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

    def stream_slices(self, sync_mode, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[MutableMapping[str, any]]]:
        """
        Override default stream_slices CDK method to provide date_slices as page chunks for data fetch.
        """
        start_date = self._from_date
        end_date = self._to_date

        # determine stream_state, if no stream_state we use start_date
        if stream_state:
            start_date = pendulum.parse(stream_state.get(self.cursor_field)).date()

        while start_date < end_date:
            # Max size of date chunks is 1 year
            # Docs: https://help.getharvest.com/api-v2/reports-api/reports/time-reports/
            end_date_slice = end_date if start_date >= end_date.subtract(years=1) else start_date.add(years=1)
            date_slice = {"from": start_date.strftime(self.date_param_template), "to": end_date_slice.strftime(self.date_param_template)}

            start_date = end_date_slice

            yield date_slice


class ExpensesClients(IncrementalReportsBase):
    """
    Docs: https://help.getharvest.com/api-v2/reports-api/reports/expense-reports/#clients-report
    """

    report_path = "expenses/clients"


class ExpensesProjects(IncrementalReportsBase):
    """
    Docs: https://help.getharvest.com/api-v2/reports-api/reports/expense-reports/#projects-report
    """

    report_path = "expenses/projects"


class ExpensesCategories(IncrementalReportsBase):
    """
    Docs: https://help.getharvest.com/api-v2/reports-api/reports/expense-reports/#expense-categories-report
    """

    report_path = "expenses/categories"


class ExpensesTeam(IncrementalReportsBase):
    """
    Docs: https://help.getharvest.com/api-v2/reports-api/reports/expense-reports/#team-report
    """

    report_path = "expenses/team"


class Uninvoiced(IncrementalReportsBase):
    """
    Docs: https://help.getharvest.com/api-v2/reports-api/reports/uninvoiced-report/
    """

    report_path = "uninvoiced"


class TimeClients(IncrementalReportsBase):
    """
    Docs: https://help.getharvest.com/api-v2/reports-api/reports/time-reports/#clients-report
    """

    report_path = "time/clients"


class TimeProjects(IncrementalReportsBase):
    """
    Docs: https://help.getharvest.com/api-v2/reports-api/reports/time-reports/#projects-report
    """

    report_path = "time/projects"


class TimeTasks(IncrementalReportsBase):
    """
    Docs: https://help.getharvest.com/api-v2/reports-api/reports/time-reports/#tasks-report
    """

    report_path = "time/tasks"


class TimeTeam(IncrementalReportsBase):
    """
    Docs: https://help.getharvest.com/api-v2/reports-api/reports/time-reports/
    """

    report_path = "time/team"


class ProjectBudget(ReportsBase):
    """
    Docs: https://help.getharvest.com/api-v2/reports-api/reports/project-budget-report/#project-budget-report
    """

    report_path = "project_budget"

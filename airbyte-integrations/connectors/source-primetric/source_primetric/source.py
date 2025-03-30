#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from datetime import date, timedelta
import json
from urllib.parse import parse_qs, urlparse
from airbyte_cdk.models import SyncMode


class PrimetricStream(HttpStream, ABC):
    url_base = "https://api.primetric.com/beta/"
    primary_key = "uuid"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page_url = response.json()["next"]
        return parse_qs(urlparse(next_page_url).query)

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["results"]

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """This method is called if we run into the rate limit.
        Rate Limits Docs: https://developer.primetric.com/#rate-limits"""
        return 31


class Assignments(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "assignments"


class Contracts(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "contracts"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["results"]


class Employees(PrimetricStream):
    primary_key = "uuid"

    def path(self, **kwargs) -> str:
        return "employees"


class EmployeesCertificates(HttpSubStream, PrimetricStream):
    primary_key = "certificate_uuid"

    def __init__(self, parent, authenticator, **kwargs):
        super().__init__(parent=parent, authenticator=authenticator, **kwargs)

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
             next_page_token: Mapping[str, Any] = None
             ) -> str:
        return f"employees/{stream_slice['uuid']}/certificates"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        uuid = str(response.url.split("employees/")[1].split("/certificates")[0])

        elements = response.json()
        if not elements:
            return
        for element in elements:
            yield {
                "employee_uuid": uuid,
                "certificate_uuid": element.get("uuid"),
                "issuer": element.get("issuer"),
                "name": element.get("name"),
                "url": element.get("url"),
                "issue_date": element.get("issue_date"),
            }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
            self,
            sync_mode: SyncMode = SyncMode.full_refresh,
            cursor_field: List[str] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:

        for employee in self.parent.read_records(sync_mode):
            yield {"uuid": employee["uuid"]}


class EmployeesContracts(HttpSubStream, PrimetricStream):
    primary_key = "contract_uuid"

    def __init__(self, parent, authenticator, **kwargs):
        super().__init__(parent=parent, authenticator=authenticator, **kwargs)

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
             next_page_token: Mapping[str, Any] = None
             ) -> str:
        return f"employees/{stream_slice['uuid']}/contracts"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        uuid = str(response.url.split("employees/")[1].split("/contracts")[0])

        elements = response.json()["results"]
        if not elements:
            return
        for element in elements:
            yield {
                "employee_uuid": uuid,
                "contract_uuid": element.get("uuid"),
                "starts_at": element.get("starts_at"),
                "ends_at": element.get("ends_at"),
                "custom_attributes": element.get("custom_attributes"),
                "employment_type": element.get("employment_type"),
                "capacity_monday": element.get("capacity_monday"),
                "capacity_tuesday": element.get("capacity_tuesday"),
                "capacity_wednesday": element.get("capacity_wednesday"),
                "capacity_thursday": element.get("capacity_thursday"),
                "capacity_friday": element.get("capacity_friday"),
                "capacity_saturday": element.get("capacity_saturday"),
                "capacity_sunday": element.get("capacity_sunday"),
                "contract_title": element.get("contract_title"),
                "total_month_cost": element.get("total_month_cost"),
                "default_hour_cost": element.get("default_hour_cost"),
                "default_hour_rate": element.get("default_hour_rate"),
                "schedule_contractor_cost": element.get("schedule_contractor_cost")
            }

    def stream_slices(
            self,
            sync_mode: SyncMode = SyncMode.full_refresh,
            cursor_field: List[str] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:

        for employee in self.parent.read_records(sync_mode):
            yield {"uuid": employee["uuid"]}


class EmployeesEntries(HttpSubStream, PrimetricStream):
    primary_key = "entry_uuid"

    def __init__(self, parent, authenticator, **kwargs):
        super().__init__(parent=parent, authenticator=authenticator, **kwargs)

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
             next_page_token: Mapping[str, Any] = None
             ) -> str:
        return f"employees/{stream_slice['uuid']}/entries"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        uuid = str(response.url.split("employees/")[1].split("/entries")[0])

        elements = response.json()
        if not elements:
            return
        for element in elements:
            yield {
                "employee_uuid": uuid,
                "entry_uuid": element.get("uuid"),
                "level": element.get("level"),
                "skill_name": element.get("skill").get("name"),
                "skill_uuid": element.get("skill").get("uuid"),
                "skill_ancestors_list": element.get("skill").get("ancestors_list")
            }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
            self,
            sync_mode: SyncMode = SyncMode.full_refresh,
            cursor_field: List[str] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for employee in self.parent.read_records(sync_mode):
            yield {"uuid": employee["uuid"]}


class EmployeesExperiences(HttpSubStream, PrimetricStream):
    primary_key = "experience_uuid"

    def __init__(self, parent, authenticator, **kwargs):
        super().__init__(parent=parent, authenticator=authenticator, **kwargs)

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
             next_page_token: Mapping[str, Any] = None
             ) -> str:
        return f"employees/{stream_slice['uuid']}/experiences"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        uuid = str(response.url.split("employees/")[1].split("/experiences")[0])

        elements = response.json()
        if not elements:
            return
        for element in elements:
            yield {
                "employee_uuid": uuid,
                "experience_uuid": element.get("uuid"),
                "position": element.get("position"),
                "project_name": element.get("project_name"),
                "industry": element.get("industry"),
                "region": element.get("region"),
                "duration": element.get("duration"),
                "work_start": element.get("work_start"),
                "work_end": element.get("work_end"),
                "desc": element.get("desc"),
                "skills": element.get("skills"),
                "skills_options": element.get("skills_options")
            }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
            self,
            sync_mode: SyncMode = SyncMode.full_refresh,
            cursor_field: List[str] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for employee in self.parent.read_records(sync_mode):
            yield {"uuid": employee["uuid"]}


class EmployeesEducation(HttpSubStream, PrimetricStream):
    primary_key = "education_uuid"

    def __init__(self, parent, authenticator, **kwargs):
        super().__init__(parent=parent, authenticator=authenticator, **kwargs)

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
             next_page_token: Mapping[str, Any] = None
             ) -> str:
        return f"employees/{stream_slice['uuid']}/education"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        uuid = str(response.url.split("employees/")[1].split("/education")[0])

        elements = response.json()
        if not elements:
            return
        for element in elements:
            yield {
                "employee_uuid": uuid,
                "education_uuid": element.get("uuid"),
                "name": element.get("name"),
                "degree": element.get("degree"),
                "starts_at": element.get("starts_at"),
                "ends_at": element.get("ends_at"),
                "description": element.get("description")
            }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
            self,
            sync_mode: SyncMode = SyncMode.full_refresh,
            cursor_field: List[str] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for employee in self.parent.read_records(sync_mode):
            yield {"uuid": employee["uuid"]}

class Hashtags(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "hash_tags"


class OrganizationClients(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "organization/clients"


class OrganizationCompanyGroups(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "organization/company_groups"


class OrganizationDepartments(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "organization/departments"


class OrganizationIdentityProviders(PrimetricStream):
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: str, **kwargs) -> Iterable[Mapping]:
        yield from json.loads(response.text)

    def path(self, **kwargs) -> str:
        return "organization/identity_providers"


class OrganizationPositions(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "organization/positions"


class OrganizationRagScopes(PrimetricStream):
    primary_key = "text"

    def path(self, **kwargs) -> str:
        return "organization/rag_scopes"


class OrganizationRoles(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "organization/roles"


class OrganizationSeniorities(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "organization/seniorities"


class OrganizationTags(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "organization/tags"


class OrganizationTeams(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "organization/teams"


class OrganizationTimeoffTypes(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "organization/timeoff_types"


class People(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "people"


class Projects(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "projects"


class ProjectsVacancies(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "projects_vacancies"


class RagRatings(PrimetricStream):
    primary_key = "project_id"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: str, **kwargs) -> Iterable[Mapping]:
        yield from json.loads(response.text)

    def path(self, **kwargs) -> str:
        return "rag_ratings"


class Timeoffs(PrimetricStream):
    def path(self, **kwargs) -> str:
        return "timeoffs"


class Worklogs(PrimetricStream):
    def __init__(self, authenticator, migration_method, migration_start_date):
        super(PrimetricStream, self).__init__(authenticator)
        self.migration_method = migration_method
        self.migration_start_date = migration_start_date

    @property
    def use_cache(self) -> bool:
        return True

    def path(self, **kwargs) -> str:
        return "worklogs/worklogs_iterator"

    def request_params(
            self,
            stream_state: Optional[Mapping[str, Any]],
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        request_params = {
            'page_size': 500
        }
        if self.migration_method == 'Migration from date' or self.migration_method == 'Migration from X last days':
            request_params = {'starts_between_min': str(self.migration_start_date),
                              'starts_between_max': str(date.today() + timedelta(days=1)),
                              'page_size': 500
                              }
        request_params.update(next_page_token if next_page_token is not None else {})

        return request_params


class SourcePrimetric(AbstractSource):
    def __init__(self):
        self.migration_method = None
        self.migration_start_date = None

    @staticmethod
    def get_connection_response(config: Mapping[str, Any]):
        token_refresh_endpoint = f'{"https://api.primetric.com/auth/token/"}'
        client_id = config["client_id"]
        client_secret = config["client_secret"]
        refresh_token = None
        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret,
                "refresh_token": refresh_token}

        try:
            response = requests.request(method="POST", url=token_refresh_endpoint, data=data, headers=headers)
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e
        return response

    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            if not config["client_secret"] or not config["client_id"]:
                raise Exception("Empty config values! Check your configuration file!")

            self.get_connection_response(config).raise_for_status()
            return True, None

        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        response = self.get_connection_response(config)
        response.raise_for_status()

        self.migration_method = config["migration_type"]["method"]

        if self.migration_method == "Migration from date":
            self.migration_start_date = config["migration_type"]["starting_migration_date"]
        elif self.migration_method == "Migration from X last days":
            last_days_to_migrate = config["migration_type"]["last_days_to_migrate"]
            self.migration_start_date = date.today() - timedelta(days=last_days_to_migrate)
        elif self.migration_method != 'Full migration':
            print("Warning unknown method detected ", self.migration_method)

        authenticator = TokenAuthenticator(response.json()["access_token"])
        employees = Employees(authenticator=authenticator)

        return [
            Assignments(authenticator=authenticator),
            Contracts(authenticator=authenticator),

            Employees(authenticator=authenticator),
            EmployeesCertificates(parent=employees, authenticator=authenticator),
            EmployeesContracts(parent=employees, authenticator=authenticator),
            EmployeesEducation(parent=employees, authenticator=authenticator),
            EmployeesEntries(parent=employees, authenticator=authenticator),
            EmployeesExperiences(parent=employees, authenticator=authenticator),

            Hashtags(authenticator=authenticator),

            OrganizationClients(authenticator=authenticator),
            OrganizationCompanyGroups(authenticator=authenticator),
            OrganizationDepartments(authenticator=authenticator),
            OrganizationIdentityProviders(authenticator=authenticator),
            OrganizationPositions(authenticator=authenticator),
            OrganizationRagScopes(authenticator=authenticator),
            OrganizationRoles(authenticator=authenticator),
            OrganizationSeniorities(authenticator=authenticator),
            OrganizationTags(authenticator=authenticator),
            OrganizationTeams(authenticator=authenticator),
            OrganizationTimeoffTypes(authenticator=authenticator),

            People(authenticator=authenticator),
            Projects(authenticator=authenticator),
            ProjectsVacancies(authenticator=authenticator),
            RagRatings(authenticator=authenticator),
            Timeoffs(authenticator=authenticator),
            Worklogs(authenticator=authenticator,
                     migration_method=self.migration_method,
                     migration_start_date=self.migration_start_date)
        ]

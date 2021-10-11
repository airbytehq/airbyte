#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Generator, List, Tuple

import backoff
import requests
from airbyte_protocol import AirbyteStream
from base_python import BaseClient
from requests.exceptions import ConnectionError
from requests.structures import CaseInsensitiveDict


class Client(BaseClient):
    API_VERSION = "3.1"

    def __init__(self, domain: str, client_id: str, client_secret: str, run_look_ids: list = []):
        """
        Note that we dynamically generate schemas for the stream__run_looks
        function because the fields returned depend on the user's look(s)
        (entered during configuration). See get_run_look_json_schema().
        """
        self.BASE_URL = f"https://{domain}/api/{self.API_VERSION}"
        self._client_id = client_id
        self._client_secret = client_secret
        self._token, self._connect_error = self.get_token()
        self._headers = {
            "Authorization": f"token {self._token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Maps Looker types to JSON Schema types for run_look JSON schema
        self._field_type_mapping = {
            "string": "string",
            "date_date": "datetime",
            "date_raw": "datetime",
            "date": "datetime",
            "date_week": "datetime",
            "date_day_of_week": "string",
            "date_day_of_week_index": "integer",
            "date_month": "string",
            "date_month_num": "integer",
            "date_month_name": "string",
            "date_day_of_month": "integer",
            "date_fiscal_month_num": "integer",
            "date_quarter": "string",
            "date_quarter_of_year": "string",
            "date_fiscal_quarter": "string",
            "date_fiscal_quarter_of_year": "string",
            "date_year": "integer",
            "date_day_of_year": "integer",
            "date_week_of_year": "integer",
            "date_fiscal_year": "integer",
            "date_time_of_day": "string",
            "date_hour": "string",
            "date_hour_of_day": "integer",
            "date_minute": "datetime",
            "date_second": "datetime",
            "date_millisecond": "datetime",
            "date_microsecond": "datetime",
            "number": "number",
            "int": "integer",
            "list": "array",
            "yesno": "boolean",
        }

        # Helpers for the self.stream__run_looks function
        self._run_look_explore_fields = {}
        self._run_looks, self._run_looks_connect_error = self.get_run_look_info(run_look_ids)

        self._dashboard_ids = []
        self._project_ids = []
        self._role_ids = []
        self._user_attribute_ids = []
        self._user_ids = []
        self._context_metadata_mapping = {"dashboards": [], "folders": [], "homepages": [], "looks": [], "spaces": []}
        super().__init__()

    @property
    def streams(self) -> Generator[AirbyteStream, None, None]:
        """
        Uses the default streams except for the run_look endpoint, where we have
        to generate its JSON Schema on the fly for the given look
        """

        streams = super().streams
        for stream in streams:
            if len(self._run_looks) > 0 and stream.name == "run_looks":
                stream.json_schema = self._get_run_look_json_schema()
            yield stream

    def get_token(self):
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        try:
            resp = requests.post(
                url=f"{self.BASE_URL}/login", headers=headers, data=f"client_id={self._client_id}&client_secret={self._client_secret}"
            )
            if resp.status_code != 200:
                return None, "Unable to connect to the Looker API. Please check your credentials."
            return resp.json()["access_token"], None
        except ConnectionError as error:
            return None, str(error)

    def get_run_look_info(self, run_look_ids):
        """
        Checks that the look IDs entered exist and can be queried
        and returns the LookML model for each (needed for JSON Schema creation)
        """
        looks = []
        for look_id in run_look_ids:
            resp = self._request(f"{self.BASE_URL}/looks/{look_id}?fields=model(id),title")
            if resp == []:
                return (
                    [],
                    f"Unable to find look {look_id}. Verify that you have entered a valid look ID and that you have permission to run it.",
                )

            looks.append((resp[0]["model"]["id"], look_id, resp[0]["title"]))

        return looks, None

    def health_check(self) -> Tuple[bool, str]:
        if self._connect_error:
            return False, self._connect_error
        elif self._run_looks_connect_error:
            return False, self._run_looks_connect_error
        return True, ""

    @backoff.on_exception(backoff.expo, requests.exceptions.ConnectionError, max_tries=7)
    def _request(self, url: str, method: str = "GET", data: dict = None) -> List[dict]:
        response = requests.request(method, url, headers=self._headers, json=data)

        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list):
                return response_data
            else:
                return [response_data]
        return []

    def _get_run_look_json_schema(self):
        """
        Generates a JSON Schema for the run_look endpoint based on the Look IDs
        entered in configuration
        """
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            "properties": {
                self._get_run_look_key(look_id, look_name): {
                    "title": look_name,
                    "properties": {field: self._get_look_field_schema(model, field) for field in self._get_look_fields(look_id)},
                    "type": ["null", "object"],
                    "additionalProperties": False,
                }
                for (model, look_id, look_name) in self._run_looks
            },
        }
        return json_schema

    def _get_run_look_key(self, look_id, look_name):
        return f"{look_id} - {look_name}"

    def _get_look_field_schema(self, model, field):
        """
        For a given LookML model and field, looks up its type and generates
        its properties for the run_look endpoint JSON Schema
        """
        explore = field.split(".")[0]

        fields = self._get_explore_fields(model, explore)

        field_type = "string"  # default to string
        for dimension in fields["dimensions"]:
            if field == dimension["name"] and dimension["type"] in self._field_type_mapping:
                field_type = self._field_type_mapping[dimension["type"]]
        for measure in fields["measures"]:
            if field == measure["name"]:
                # Default to number except for list, date, and yesno
                field_type = "number"
                if measure["type"] in self._field_type_mapping:
                    field_type = self._field_type_mapping[measure["type"]]

        if field_type == "datetime":
            # no datetime type for JSON Schema
            return {"type": ["null", "string"], "format": "date-time"}

        return {"type": ["null", field_type]}

    def _get_explore_fields(self, model, explore):
        """
        For a given LookML model and explore, looks up its dimensions/measures
        and their types for run_look endpoint JSON Schema generation
        """
        if (model, explore) not in self._run_look_explore_fields:
            self._run_look_explore_fields[(model, explore)] = self._request(
                f"{self.BASE_URL}/lookml_models/{model}/explores/{explore}?fields=fields(dimensions(name,type),measures(name,type))"
            )[0]["fields"]

        return self._run_look_explore_fields[(model, explore)]

    def _get_look_fields(self, look_id) -> List[str]:
        return self._request(f"{self.BASE_URL}/looks/{look_id}?fields=query(fields)")[0]["query"]["fields"]

    def _get_dashboard_ids(self) -> List[int]:
        if not self._dashboard_ids:
            self._dashboard_ids = [obj["id"] for obj in self._request(f"{self.BASE_URL}/dashboards") if isinstance(obj["id"], int)]
        return self._dashboard_ids

    def _get_project_ids(self) -> List[int]:
        if not self._project_ids:
            self._project_ids = [obj["id"] for obj in self._request(f"{self.BASE_URL}/projects")]
        return self._project_ids

    def _get_user_ids(self) -> List[int]:
        if not self._user_ids:
            self._user_ids = [obj["id"] for obj in self._request(f"{self.BASE_URL}/users")]
        return self._user_ids

    def stream__color_collections(self, fields):
        yield from self._request(f"{self.BASE_URL}/color_collections")

    def stream__connections(self, fields):
        yield from self._request(f"{self.BASE_URL}/connections")

    def stream__dashboards(self, fields):
        dashboards_list = [obj for obj in self._request(f"{self.BASE_URL}/dashboards") if isinstance(obj["id"], int)]
        self._dashboard_ids = [obj["id"] for obj in dashboards_list]
        self._context_metadata_mapping["dashboards"] = [
            obj["content_metadata_id"] for obj in dashboards_list if isinstance(obj["content_metadata_id"], int)
        ]
        yield from dashboards_list

    def stream__dashboard_elements(self, fields):
        for dashboard_id in self._get_dashboard_ids():
            yield from self._request(f"{self.BASE_URL}/dashboards/{dashboard_id}/dashboard_elements")

    def stream__dashboard_filters(self, fields):
        for dashboard_id in self._get_dashboard_ids():
            yield from self._request(f"{self.BASE_URL}/dashboards/{dashboard_id}/dashboard_filters")

    def stream__dashboard_layouts(self, fields):
        for dashboard_id in self._get_dashboard_ids():
            yield from self._request(f"{self.BASE_URL}/dashboards/{dashboard_id}/dashboard_layouts")

    def stream__datagroups(self, fields):
        yield from self._request(f"{self.BASE_URL}/datagroups")

    def stream__folders(self, fields):
        folders_list = self._request(f"{self.BASE_URL}/folders")
        self._context_metadata_mapping["folders"] = [
            obj["content_metadata_id"] for obj in folders_list if isinstance(obj["content_metadata_id"], int)
        ]
        yield from folders_list

    def stream__groups(self, fields):
        yield from self._request(f"{self.BASE_URL}/groups")

    def stream__homepages(self, fields):
        homepages_list = self._request(f"{self.BASE_URL}/homepages")
        self._context_metadata_mapping["homepages"] = [
            obj["content_metadata_id"] for obj in homepages_list if isinstance(obj["content_metadata_id"], int)
        ]
        yield from homepages_list

    def stream__integration_hubs(self, fields):
        yield from self._request(f"{self.BASE_URL}/integration_hubs")

    def stream__integrations(self, fields):
        yield from self._request(f"{self.BASE_URL}/integrations")

    def stream__lookml_dashboards(self, fields):
        lookml_dashboards_list = [obj for obj in self._request(f"{self.BASE_URL}/dashboards") if isinstance(obj["id"], str)]
        yield from lookml_dashboards_list

    def stream__lookml_models(self, fields):
        yield from self._request(f"{self.BASE_URL}/lookml_models")

    def stream__looks(self, fields):
        looks_list = self._request(f"{self.BASE_URL}/looks")
        self._context_metadata_mapping["looks"] = [
            obj["content_metadata_id"] for obj in looks_list if isinstance(obj["content_metadata_id"], int)
        ]
        yield from looks_list

    def stream__model_sets(self, fields):
        yield from self._request(f"{self.BASE_URL}/model_sets")

    def stream__permission_sets(self, fields):
        yield from self._request(f"{self.BASE_URL}/permission_sets")

    def stream__permissions(self, fields):
        yield from self._request(f"{self.BASE_URL}/permissions")

    def stream__projects(self, fields):
        projects_list = self._request(f"{self.BASE_URL}/projects")
        self._project_ids = [obj["id"] for obj in projects_list]
        yield from projects_list

    def stream__project_files(self, fields):
        for project_id in self._get_project_ids():
            yield from self._request(f"{self.BASE_URL}/projects/{project_id}/files")

    def stream__git_branches(self, fields):
        for project_id in self._get_project_ids():
            yield from self._request(f"{self.BASE_URL}/projects/{project_id}/git_branches")

    def stream__roles(self, fields):
        roles_list = self._request(f"{self.BASE_URL}/roles")
        self._role_ids = [obj["id"] for obj in roles_list]
        yield from roles_list

    def stream__role_groups(self, fields):
        if not self._role_ids:
            self._role_ids = [obj["id"] for obj in self._request(f"{self.BASE_URL}/roles")]
        for role_id in self._role_ids:
            yield from self._request(f"{self.BASE_URL}/roles/{role_id}/groups")

    def stream__run_looks(self, fields):
        for (model, look_id, look_name) in self._run_looks:
            yield from [
                {self._get_run_look_key(look_id, look_name): row} for row in self._request(f"{self.BASE_URL}/looks/{look_id}/run/json")
            ]

    def stream__scheduled_plans(self, fields):
        yield from self._request(f"{self.BASE_URL}/scheduled_plans?all_users=true")

    def stream__spaces(self, fields):
        spaces_list = self._request(f"{self.BASE_URL}/spaces")
        self._context_metadata_mapping["spaces"] = [
            obj["content_metadata_id"] for obj in spaces_list if isinstance(obj["content_metadata_id"], int)
        ]
        yield from spaces_list

    def stream__user_attributes(self, fields):
        user_attributes_list = self._request(f"{self.BASE_URL}/user_attributes")
        self._user_attribute_ids = [obj["id"] for obj in user_attributes_list]
        yield from user_attributes_list

    def stream__user_attribute_group_values(self, fields):
        if not self._user_attribute_ids:
            self._user_attribute_ids = [obj["id"] for obj in self._request(f"{self.BASE_URL}/user_attributes")]
        for user_attribute_id in self._user_attribute_ids:
            yield from self._request(f"{self.BASE_URL}/user_attributes/{user_attribute_id}/group_values")

    def stream__user_login_lockouts(self, fields):
        yield from self._request(f"{self.BASE_URL}/user_login_lockouts")

    def stream__users(self, fields):
        users_list = self._request(f"{self.BASE_URL}/users")
        self._user_ids = [obj["id"] for obj in users_list]
        yield from users_list

    def stream__user_attribute_values(self, fields):
        for user_ids in self._get_user_ids():
            yield from self._request(f"{self.BASE_URL}/users/{user_ids}/attribute_values?all_values=true&include_unset=true")

    def stream__user_sessions(self, fields):
        for user_ids in self._get_user_ids():
            yield from self._request(f"{self.BASE_URL}/users/{user_ids}/sessions")

    def stream__versions(self, fields):
        yield from self._request(f"{self.BASE_URL}/versions")

    def stream__workspaces(self, fields):
        yield from self._request(f"{self.BASE_URL}/workspaces")

    def stream__query_history(self, fields):
        request_data = {
            "model": "i__looker",
            "view": "history",
            "fields": [
                "query.id",
                "history.created_date",
                "query.model",
                "query.view",
                "space.id",
                "look.id",
                "dashboard.id",
                "user.id",
                "history.query_run_count",
                "history.total_runtime",
            ],
            "filters": {"query.model": "-EMPTY", "history.runtime": "NOT NULL", "user.is_looker": "No"},
            "sorts": [
                "-history.created_date" "query.id",
            ],
        }
        history_list = self._request(f"{self.BASE_URL}/queries/run/json?limit=10000", method="POST", data=request_data)
        for history_data in history_list:
            yield {k.replace(".", "_"): v for k, v in history_data.items()}

    def stream__content_metadata(self, fields):
        yield from self._metadata_processing(f"{self.BASE_URL}/content_metadata/")

    def stream__content_metadata_access(self, fields):
        yield from self._metadata_processing(f"{self.BASE_URL}/content_metadata_access?content_metadata_id=")

    def _metadata_processing(self, url: str):
        content_metadata_id_list = []
        for metadata_main_obj, ids in self._context_metadata_mapping.items():
            if not ids:
                metadata_id_list = [
                    obj["content_metadata_id"]
                    for obj in self._request(f"{self.BASE_URL}/{metadata_main_obj}")
                    if isinstance(obj["content_metadata_id"], int)
                ]
                self._context_metadata_mapping[metadata_main_obj] = metadata_id_list
                content_metadata_id_list += metadata_id_list
            else:
                content_metadata_id_list += ids

        for metadata_id in set(content_metadata_id_list):
            yield from self._request(f"{url}{metadata_id}")

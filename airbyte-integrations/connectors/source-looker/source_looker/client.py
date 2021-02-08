"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import List, Tuple

import backoff
import requests
from base_python import BaseClient
from requests.exceptions import ConnectionError
from requests.structures import CaseInsensitiveDict


class Client(BaseClient):
    API_VERSION = "3.1"

    def __init__(self, domain: str, client_id: str, client_secret: str):
        self.BASE_URL = f"https://{domain}/api/{self.API_VERSION}"
        self._client_id = client_id
        self._client_secret = client_secret
        self._token, self._connect_error = self.get_token()
        self._headers = {
            "Authorization": f"token {self._token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self._dashboard_ids = []
        self._project_ids = []
        self._role_ids = []
        self._user_attribute_ids = []
        self._user_ids = []
        self._context_metadata_mapping = {"dashboards": [], "folders": [], "homepages": [], "looks": [], "spaces": []}
        super().__init__()

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

    def health_check(self) -> Tuple[bool, str]:
        if self._connect_error:
            return False, self._connect_error
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

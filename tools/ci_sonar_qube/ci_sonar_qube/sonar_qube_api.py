import re
from functools import reduce
from typing import Mapping, Any, Optional
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth

from ci_common_utils import Logger

AIRBYTE_PROJECT_PREFIX = "airbyte"


class SonarQubeApi:
    """https://sonarcloud.io/web_api"""
    logger = Logger()

    def __init__(self, host: str, token: str, pr_name: str):

        self._host = host
        self._token = token

        # split the latest name part
        self._pr_id = (pr_name or '').split("/")[-1]
        if not self._pr_id.isdigit():
            self.logger.critical(f"PR id should be integer. Current value: {pr_name}")
        self._pr_id = int(self._pr_id)
        # check token
        # https://sonarcloud.io/web_api/api/authentication/validate
        if not self._host:
            return
        resp = self.__get("authentication/validate")
        if not resp["valid"]:
            self.logger.critical("provided token is not valid")

    @property
    def __auth(self):
        return HTTPBasicAuth(self._token, '')

    def __parse_response(self, url: str, response: requests.Response) -> Mapping[str, Any]:
        if response.status_code == 204:
            # empty response
            return {}
        elif response.status_code != 200:
            self.logger.critical(f"API error for {url}: [{response.status_code}] {response.json()['errors']}")
        return response.json()

    def generate_url(self, endpoint: str) -> str:
        return reduce(urljoin, [self._host, "/api/", endpoint])

    def __post(self, endpoint: str, json: Mapping[str, Any]) -> Mapping[str, Any]:
        url = self.generate_url(endpoint)
        return self.__parse_response(url, requests.post(url, auth=self.__auth, params=json, json=json))

    def __get(self, endpoint: str) -> Mapping[str, Any]:
        url = self.generate_url(endpoint)
        return self.__parse_response(url, requests.get(url, auth=self.__auth))

    @classmethod
    def module2project(cls, module_name: str) -> str:
        """"""
        parts = module_name.split("/")
        if len(parts) != 2:
            cls.logger.critical("module name must have the format: component/module")
        return f"{AIRBYTE_PROJECT_PREFIX}:{parts[0].lower()}:{parts[1].lower().replace('_', '-')}"

    def __correct_project_name(self, project_name: str) -> str:
        return f"{project_name}:{self._pr_id}" if self._pr_id else project_name

    def __search_project(self, project_name: str) -> Optional[Mapping[str, Any]]:
        """https://sonarcloud.io/web_api/api/projects/search"""
        data = self.__get(f"projects/search?q={project_name}")
        exists_projects = data["components"]
        if len(exists_projects) > 1:
            self.logger.critical(f"there are several projects with the name '{project_name}'")
        elif len(exists_projects) == 0:
            return None
        return exists_projects[0]

    def prepare_project_settings(self, project_name: str) -> Mapping[str, str]:
        title = re.sub('[:_-]', ' ', project_name).title()
        if self._pr_id:
            title += f"(#{self._pr_id})"

        project_name = self.__correct_project_name(project_name)
        return {
            "name": title,
            "project": project_name,
            "visibility": "private",
        }

    def create_project(self, project_name: str) -> bool:
        """https://sonarcloud.io/web_api/api/projects/create"""
        data = self.prepare_project_settings(project_name)
        project_name = data["project"]
        exists_project = self.__search_project(project_name)
        if exists_project:
            self.logger.info(f"The project '{project_name}' was created before")
            return True

        self.__post("projects/create", data)
        self.logger.info(f"The project '{project_name}' was created")
        return True

    def remove_project(self, project_name: str) -> bool:
        """https://sonarcloud.io/web_api/api/projects/delete"""
        project_name = self.prepare_project_settings(project_name)["project"]
        exists_project = self.__search_project(project_name)
        if exists_project is None:
            self.logger.info(f"not found the project '{project_name}'")
            return True
        body = {
            "project": project_name
        }
        self.__post("projects/delete", body)
        self.logger.info(f"The project '{project_name}' was removed")
        return True

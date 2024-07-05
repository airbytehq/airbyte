#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .streams import API_VERSION, ContentMetadata, Dashboards, LookerException, LookerStream, QueryHistory, RunLooks, SwaggerParser


class CustomTokenAuthenticator(TokenAuthenticator):
    def __init__(self, domain: str, client_id: str, client_secret: str):
        self._domain, self._client_id, self._client_secret = domain, client_id, client_secret
        super().__init__(None)

        self._access_token = None
        self._token_expiry_date = pendulum.now()

    def update_access_token(self) -> Optional[str]:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        url = f"https://{self._domain}/api/{API_VERSION}/login"
        try:
            resp = requests.post(url=url, headers=headers, data=f"client_id={self._client_id}&client_secret={self._client_secret}")
            if resp.status_code != 200:
                return "Unable to connect to the Looker API. Please check your credentials."
        except ConnectionError as error:
            return str(error)
        data = resp.json()
        self._access_token = data["access_token"]
        self._token_expiry_date = pendulum.now().add(seconds=data["expires_in"])
        return None

    def get_auth_header(self) -> Mapping[str, Any]:
        if self._token_expiry_date < pendulum.now():
            err = self.update_access_token()
            if err:
                raise LookerException(f"auth error: {err}")
        return {"Authorization": f"token {self._access_token}"}


class SourceLooker(AbstractSource):
    """
    Source Intercom fetch data from messaging platform.
    """

    def get_authenticator(self, config: Mapping[str, Any]) -> CustomTokenAuthenticator:
        return CustomTokenAuthenticator(domain=config["domain"], client_id=config["client_id"], client_secret=config["client_secret"])

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        authenticator = self.get_authenticator(config)
        err = authenticator.update_access_token()
        if err:
            logging.getLogger("airbyte").error("auth error: {err}")
            return False, err
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        base_args = {
            "authenticator": self.get_authenticator(config),
            "domain": config["domain"],
        }
        args = dict(swagger_parser=SwaggerParser(domain=config["domain"]), **base_args)

        streams = [
            LookerStream("color_collections", **args),
            LookerStream("connections", **args),
            ContentMetadata("content_metadata", **args),
            ContentMetadata("content_metadata_access", **args),
            Dashboards("dashboards", **args),
            LookerStream("dashboard_elements", **args),
            LookerStream("dashboard_filters", **args),
            LookerStream("dashboard_layout_components", **args),
            LookerStream("dashboard_layouts", **args),
            LookerStream("datagroups", **args),
            LookerStream("folders", **args),
            LookerStream("folder_ancestors", **args),
            LookerStream("git_branches", **args),
            LookerStream("groups", **args),
            LookerStream("homepage_items", **args),
            LookerStream("homepage_sections", **args),
            LookerStream("homepages", **args),
            LookerStream("integration_hubs", **args),
            LookerStream("integrations", **args),
            LookerStream("legacy_features", **args),
            Dashboards("lookml_dashboards", **args),
            LookerStream("lookml_models", **args),
            LookerStream("looks", **args),
            LookerStream("model_sets", **args),
            LookerStream("permission_sets", **args),
            LookerStream("permissions", **args),
            LookerStream("primary_homepage_sections", **args),
            LookerStream("projects", **args),
            LookerStream("project_files", **args),
            QueryHistory(**base_args),
            LookerStream("roles", **args),
            LookerStream("role_groups", **args),
            RunLooks(run_look_ids=config["run_look_ids"], **args) if config.get("run_look_ids") else None,
            LookerStream("scheduled_plans", request_params={"all_users": "true"}, **args),
            LookerStream("spaces", **args),
            LookerStream("space_ancestors", **args),
            LookerStream("user_attributes", **args),
            LookerStream("user_attribute_group_values", **args),
            LookerStream("user_attribute_values", request_params={"all_values": "true", "include_unset": "true"}, **args),
            LookerStream("user_login_lockouts", **args),
            LookerStream("user_sessions", **args),
            LookerStream("users", **args),
            LookerStream("versions", **args),
            LookerStream("workspaces", **args),
        ]
        # stream  RunLooks is dynamic and will be added if run_look_ids is not empty
        # but we need to save streams' older
        return [stream for stream in streams if stream]

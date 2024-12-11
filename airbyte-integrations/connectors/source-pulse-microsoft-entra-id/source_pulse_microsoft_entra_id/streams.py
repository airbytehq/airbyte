import logging
from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .auth import get_token
from .transformation import TransformationMixin

logger = logging.getLogger("airbyte")


class MicrosoftGraphStream(HttpStream, ABC):

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(authenticator=TokenAuthenticator(token=get_token(config)))
        self.config = config
        self._delta_token = None
        self._state = {}

    url_base = "https://graph.microsoft.com/v1.0/"
    primary_key = "id"
    none_existing_id = "0123456789"

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        return 1000

    @property
    def cursor_field(self) -> str:
        return "id"

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        self._state = value or {}
        if "delta_token" in value:
            self._delta_token = value["delta_token"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response = response.json()

        # Check for deltaLink which indicates end of pagination
        if "@odata.deltaLink" in json_response:
            delta_link = json_response["@odata.deltaLink"]
            if "$deltatoken=" in delta_link:
                self._delta_token = delta_link.split("$deltatoken=")[1].split("&")[0]
            return None

        # Check for nextLink which contains skiptoken for pagination
        if "@odata.nextLink" in json_response:
            next_link = json_response["@odata.nextLink"]
            if "$skiptoken=" in next_link:
                skiptoken = next_link.split("$skiptoken=")[1].split("&")[0]
                return {"$skiptoken": skiptoken}

        return None

    def request_params(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {}

        # If we have a stored delta token in state, use it
        if stream_state and stream_state.get("delta_token"):
            params["$deltatoken"] = stream_state["delta_token"]

        # If we're paginating, add the skiptoken
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get("value", [])

        for record in records:
            if "@removed" in record:
                record["entity_deleted"] = "true"
                del record["@removed"]
            yield record

    def read_records(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        try:
            self._delta_token = stream_state.get("delta_token") if stream_state else None

            for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
                yield record

            if self._delta_token:
                self.state = {"delta_token": self._delta_token}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Resource not found for: {e.response.url}. Skipping.")
                return
            raise e

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 404:
            logger.warning(f"Resource not found: {response.json()}. Ignoring 404 for this request.")
            return False

        return super().should_retry(response)


class ParentChildStream(MicrosoftGraphStream, ABC):
    """
    Generic child stream that inherits from the MicrosoftGraphStream for working with a parent-child stream relationship.
    """
    parent_stream_class = None
    parent_id_field = None

    def stream_slices(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if not self.parent_stream_class or not self.parent_id_field:
            raise ValueError("Must define 'parent_stream_class' and 'parent_id_field' for child streams")

        parent_stream = self.parent_stream_class(config=self.config)
        for parent_record in parent_stream.read_records(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state):
            parent_id = parent_record.get(self.parent_id_field)
            if parent_id:
                yield {"parent_id": parent_id}
            else:
                logger.warning(f"Missing parent_id field {self.parent_id_field} in parent record: {parent_record}")


class Users(MicrosoftGraphStream):
    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh", "incremental"]

    def path(self, **kwargs) -> str:
        return "users/delta?$select=businessPhones,displayName,givenName,jobTitle,mail,mobilePhone,officeLocation,preferredLanguage,surname,userPrincipalName,id,userType"


class Groups(MicrosoftGraphStream):
    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh", "incremental"]

    def path(self, **kwargs) -> str:
        return "groups/delta"


class Applications(MicrosoftGraphStream):
    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh", "incremental"]

    def path(self, **kwargs) -> str:
        return "applications/delta"


class DirectoryRoles(MicrosoftGraphStream):
    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh", "incremental"]

    def path(self, **kwargs) -> str:
        return "directoryRoles/delta"


class ServicePrincipals(MicrosoftGraphStream):
    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh", "incremental"]

    def path(self, **kwargs) -> str:
        return "servicePrincipals/delta"


class AccessPackages(MicrosoftGraphStream):  # TODO timestamp doesnt work. will use full append for now
    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh", "incremental"]

    @property
    def cursor_field(self) -> str:
        return "modifiedDateTime"

    def path(self, **kwargs) -> str:
        return "identityGovernance/entitlementManagement/accessPackages"

    def request_params(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {}

        if stream_state and stream_state.get("modifiedDateTime"):
            formatted_date = datetime.strptime(stream_state["modifiedDateTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_date_str = formatted_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            filter_query = f"modifiedDateTime gt {formatted_date_str}"
            params["$filter"] = filter_query

        if next_page_token:
            params.update(next_page_token)

        return params

    def read_records(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        try:
            latest_cursor_value = stream_state.get("modifiedDateTime") if stream_state else None

            for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
                yield record

                if "modifiedDateTime" in record:
                    record_cursor_value = record["modifiedDateTime"]
                    latest_cursor_value = max(latest_cursor_value or "", record_cursor_value)

            if latest_cursor_value:
                self.state = {"modifiedDateTime": latest_cursor_value}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Resource not found for: {e.response.url}. Skipping.")
                return
            raise e


class AccessPackageResources(ParentChildStream):
    parent_stream_class = AccessPackages
    parent_id_field = "id"

    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh", "incremental"]

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        if not stream_slice or "parent_id" not in stream_slice:
            return f"identityGovernance/entitlementManagement/accessPackages/{self.none_existing_id}?$expand=resourceRoleScopes($expand=role,scope)"
        parent_id = stream_slice["parent_id"]
        return f"identityGovernance/entitlementManagement/accessPackages/{parent_id}?$expand=resourceRoleScopes($expand=role,scope)"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()


class AccessPackageMembers(ParentChildStream, TransformationMixin):
    parent_stream_class = AccessPackages
    parent_id_field = "id"

    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh"]

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        if not stream_slice or "parent_id" not in stream_slice:
            return f"identityGovernance/entitlementManagement/assignments?$filter=accessPackage/id eq '{self.none_existing_id}'&$expand=target"
        parent_id = stream_slice["parent_id"]
        return f"identityGovernance/entitlementManagement/assignments?$filter=accessPackage/id eq '{parent_id}'&$expand=target"

    def transform_record(self, record: MutableMapping[str, Any], stream_slice: Optional[Mapping[str, Any]] = None) -> Mapping[str, Any]:
        if stream_slice and "parent_id" in stream_slice:
            record["accessPackageId"] = stream_slice["parent_id"]
        return record


class DirectoryAudits(MicrosoftGraphStream):
    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh", "incremental"]

    def path(self, **kwargs) -> str:
        return "auditLogs/directoryAudits"

    @property
    def cursor_field(self) -> str:
        return "activityDateTime"

    def request_params(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {}

        if stream_state and stream_state.get("activityDateTime"):
            params["$filter"] = f"activityDateTime gt {stream_state['activityDateTime']}"

        if next_page_token:
            params.update(next_page_token)

        return params

    def read_records(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        try:
            latest_cursor_value = stream_state.get("activityDateTime") if stream_state else None

            for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
                yield record

                if "activityDateTime" in record:
                    record_cursor_value = record["activityDateTime"]
                    latest_cursor_value = max(latest_cursor_value or "", record_cursor_value)

            if latest_cursor_value:
                self.state = {"activityDateTime": latest_cursor_value}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Resource not found for: {e.response.url}. Skipping.")
                return
            raise e


class DirectoryRoleTemplates(MicrosoftGraphStream):  # no incremental ability. ok to override
    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh"]

    def path(self, **kwargs) -> str:
        return "directoryRoleTemplates"


class AppRolesAssignedTo(ParentChildStream):
    parent_stream_class = ServicePrincipals
    parent_id_field = "id"

    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh"]

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        if not stream_slice or "parent_id" not in stream_slice:
            return f"servicePrincipals/{self.none_existing_id}/appRoleAssignedTo"
        parent_id = stream_slice["parent_id"]
        return f"servicePrincipals/{parent_id}/appRoleAssignedTo" if parent_id else "servicePrincipals/appRoleAssignedTo"


class ApplicationOwners(ParentChildStream, TransformationMixin):
    parent_stream_class = Applications
    parent_id_field = "id"

    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh"]

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        if not stream_slice or "parent_id" not in stream_slice:
            return f"applications/{self.none_existing_id}/owners"
        parent_id = stream_slice["parent_id"]
        return f"applications/{parent_id}/owners"

    def transform_record(self, record: MutableMapping[str, Any], stream_slice: Optional[Mapping[str, Any]] = None) -> Mapping[str, Any]:
        if stream_slice and "parent_id" in stream_slice:
            record["applicationId"] = stream_slice["parent_id"]
        return record


class Catalogs(MicrosoftGraphStream):  # TODO timestamp doesnt work. will use full append for now
    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh", "incremental"]

    @property
    def cursor_field(self) -> str:
        return "modifiedDateTime"

    def path(self, **kwargs) -> str:
        return "identityGovernance/entitlementManagement/catalogs"

    def request_params(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {}

        if stream_state and stream_state.get("modifiedDateTime"):
            formatted_date = datetime.strptime(stream_state["modifiedDateTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_date_str = formatted_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            filter_query = f"modifiedDateTime gt {formatted_date_str}"
            params["$filter"] = filter_query

        if next_page_token:
            params.update(next_page_token)

        return params

    def read_records(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        try:
            latest_cursor_value = stream_state.get("modifiedDateTime") if stream_state else None

            for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
                yield record

                if "modifiedDateTime" in record:
                    record_cursor_value = record["modifiedDateTime"]
                    latest_cursor_value = max(latest_cursor_value or "", record_cursor_value)

            if latest_cursor_value:
                self.state = {"modifiedDateTime": latest_cursor_value}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Resource not found for: {e.response.url}. Skipping.")
                return
            raise e


class DirectoryRolesPermissions(ParentChildStream, TransformationMixin):
    parent_stream_class = DirectoryRoleTemplates
    parent_id_field = "id"

    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh"]

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        if not stream_slice or "parent_id" not in stream_slice:
            return f"roleManagement/directory/roleDefinitions/{self.none_existing_id}"
        parent_id = stream_slice["parent_id"]
        return f"roleManagement/directory/roleDefinitions/{parent_id}"

    def transform_record(self, record: MutableMapping[str, Any], stream_slice: Optional[Mapping[str, Any]] = None) -> Mapping[str, Any]:
        if stream_slice and "parent_id" in stream_slice:
            record["permissions"] = "rolePer"
        return record

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()


class UserMembershipInGroupsAndDirectory(ParentChildStream, TransformationMixin):
    parent_stream_class = Users
    parent_id_field = "id"

    @property
    def supported_sync_modes(self) -> List[str]:
        return ["full_refresh"]

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        if not stream_slice or "parent_id" not in stream_slice:
            return f"users/{self.none_existing_id}/transitiveMemberOf"
        parent_id = stream_slice["parent_id"]
        return f"users/{parent_id}/transitiveMemberOf"

    def transform_record(self, record: MutableMapping[str, Any], stream_slice: Optional[Mapping[str, Any]] = None) -> Mapping[str, Any]:
        if stream_slice and "parent_id" in stream_slice:
            record["userId"] = stream_slice["parent_id"]
        return record

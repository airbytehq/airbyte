import logging
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, Optional, MutableMapping  # Added MutableMapping
from datetime import datetime

from airbyte_cdk.sources.streams import Stream

from .base import BaseAwsClient

logger = logging.getLogger("airbyte")


class BaseIamStream(Stream, ABC):
    primary_key: str = None
    name: str = None
    pagination_function: str = None
    max_items_per_page: int = 100

    def __init__(self, config: Mapping[str, Any]):
        super().__init__()
        self.config = config
        self.aws_client = BaseAwsClient(config)
        self.client = self.aws_client.get_iam_client()
        self.cloudtrail_client = self.aws_client.get_cloudtrail_client()
        self.org_client = self.aws_client.get_organizations_client()
        self.access_analyzer_client = self.aws_client.get_access_analyzer_client()

    def next_page_token(self, response: Dict[str, Any]) -> Optional[Mapping[str, Any]]:
        marker = response.get('Marker')
        if marker:
            return {'Marker': marker}
        return None

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"MaxItems": self.max_items_per_page}
        if next_page_token:
            params.update(next_page_token)
        return params

    def read_records(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None
    ) -> Iterable[Mapping[str, Any]]:
        if not self.pagination_function:
            raise NotImplementedError("pagination_function must be defined")

        try:
            stream_state = stream_state or {}
            pagination_args = self.request_params(
                stream_state=stream_state,
                stream_slice=stream_slice
            )

            while True:
                response = getattr(self.client, self.pagination_function)(**pagination_args)
                yield from self.extract_records(response)

                next_page_token = self.next_page_token(response)
                if not next_page_token:
                    break

                pagination_args.update(next_page_token)

        except Exception as e:
            logger.error(f"Error fetching {self.name}: {str(e)}")
            yield from []

    def extract_records(self, response: Dict) -> List[Dict]:
        return response.get(self.name.title(), [])

class ParentChildIamStream(BaseIamStream, ABC):
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
        for parent_record in parent_stream.read_records(sync_mode=sync_mode):
            parent_id = parent_record.get(self.parent_id_field)
            if parent_id:
                yield {"parent_id": parent_id, "parent_record": parent_record}
            else:
                logger.warning(f"Missing parent_id field {self.parent_id_field} in parent record: {parent_record}")

class UsersStream(BaseIamStream):
    primary_key = "UserId"
    name = "users"
    pagination_function = "list_users"

class GroupsStream(BaseIamStream):
    primary_key = "GroupId"
    name = "groups"
    pagination_function = "list_groups"

class RolesStream(BaseIamStream):
    primary_key = "RoleId"
    name = "roles"
    pagination_function = "list_roles"

class PoliciesStream(BaseIamStream):
    primary_key = "PolicyId"
    name = "policies"
    pagination_function = "list_policies"

class AccessKeysStream(ParentChildIamStream):
    primary_key = "AccessKeyId"
    name = "access_keys"
    parent_stream_class = UsersStream
    parent_id_field = "UserName"
    max_items_per_page = 100

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"MaxItems": self.max_items_per_page}
        if next_page_token:
            params.update(next_page_token)
        if stream_slice and stream_slice.get("parent_id"):
            params["UserName"] = stream_slice["parent_id"]
        return params

    def read_records(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None
    ) -> Iterable[Mapping[str, Any]]:
        parent_id = stream_slice.get("parent_id") if stream_slice else None
        if not parent_id:
            return

        try:
            pagination_args = self.request_params(
                stream_state=stream_state or {},
                stream_slice=stream_slice
            )

            while True:
                try:
                    response = self.client.list_access_keys(**pagination_args)
                    records = response.get('AccessKeyMetadata', [])
                    if records:
                        for record in records:
                            record['UserName'] = parent_id
                            yield record

                    next_page_token = self.next_page_token(response)
                    if not next_page_token:
                        break

                    pagination_args.update(next_page_token)

                except self.client.exceptions.NoSuchEntityException:
                    logger.warning(f"User {parent_id} not found")
                    break
                except Exception as e:
                    logger.error(f"Error fetching access keys for user {parent_id}: {str(e)}")
                    break

        except Exception as e:
            logger.error(f"Error in read_records: {str(e)}")
            yield from []

class CloudTrailEventsStream(BaseIamStream):
    primary_key = "EventId"
    name = "cloudtrail_events"
    max_items_per_page = 50

    AUTH_EVENT_NAMES = {
        "AssumeRole",
        "AssumeRoleWithSAML",
        "ConsoleLogin",
        "CreateSession",
        "SwitchRole",
        "ExitRole",
        "GetSSOStatus",
        "StartSSO",
        "AssumeRoot",
        "CreateLoginProfile",
        "GetLoginProfile",
        "GetCallerIdentity",
        "CredentialChallenge",
        "CredentialVerification"
    }

    @property
    def cursor_field(self) -> str:
        return "EventTime"

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        self._state = value or {}

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(config)
        self._state = {}

    def next_page_token(self, response: Dict[str, Any]) -> Optional[Mapping[str, Any]]:
        next_token = response.get('NextToken')
        if next_token:
            return {'NextToken': next_token}
        return None

    def get_lookup_attributes(self, stream_state: Mapping[str, Any]) -> Dict:
        attrs = {}
        start_time_str = stream_state.get("EventTime") or self.config.get('provider', {}).get('start_time')

        if start_time_str:
            try:
                attrs['StartTime'] = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ")
            except Exception as e:
                logger.error(f"Error parsing StartTime from stream_state or config: {e}")
        else:
            logger.warning("No StartTime found in stream_state or config, defaulting to no start time")

        logger.info(f"CloudTrail lookup attributes - StartTime: {attrs.get('StartTime')}")
        return attrs

    def is_auth_event(self, event: Dict[str, Any]) -> bool:
        event_name = event.get('EventName')
        return event_name in self.AUTH_EVENT_NAMES

    def read_records(self, sync_mode: str, cursor_field: List[str] = None,
                     stream_slice: Mapping[str, Any] = None,
                     stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        try:
            stream_state = stream_state or {}
            lookup_attrs = self.get_lookup_attributes(stream_state)
            paginator = self.cloudtrail_client.get_paginator('lookup_events')

            for page in paginator.paginate(**lookup_attrs):
                for event in page.get('Events', []):
                    if self.is_auth_event(event):
                        yield event
        except Exception as e:
            logger.error(f"Error fetching CloudTrail events: {str(e)}", exc_info=True)
            yield from []

class AccessAnalyzersStream(BaseIamStream):
    primary_key = "arn"
    name = "analyzers"
    max_items_per_page = 50

    def next_page_token(self, response: Dict[str, Any]) -> Optional[Mapping[str, Any]]:
        next_token = response.get('nextToken')
        if next_token:
            return {'nextToken': next_token}
        return None

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            pagination_args = {'maxResults': self.max_items_per_page}

            while True:
                response = self.access_analyzer_client.list_analyzers(**pagination_args)
                yield from response['analyzers']

                next_page_token = self.next_page_token(response)
                if not next_page_token:
                    break

                pagination_args.update(next_page_token)

        except Exception as e:
            logger.error(f"Error listing Access Analyzers: {str(e)}")
            yield from []

class AnalyzerFindingsStream(ParentChildIamStream):
    primary_key = "id"
    name = "analyzer_findings"
    parent_stream_class = AccessAnalyzersStream
    parent_id_field = "arn"
    max_items_per_page = 50

    def next_page_token(self, response: Dict[str, Any]) -> Optional[Mapping[str, Any]]:
        next_token = response.get('nextToken')
        if next_token:
            return {'nextToken': next_token}
        return None

    def read_records(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        parent_id = stream_slice.get("parent_id") if stream_slice else None
        if not parent_id:
            return

        try:
            pagination_args = {
                'analyzerArn': parent_id,
                'maxResults': self.max_items_per_page
            }

            while True:
                response = self.access_analyzer_client.list_findings(**pagination_args)
                for finding in response['findings']:
                    finding["analyzer_arn"] = parent_id
                    yield finding

                next_page_token = self.next_page_token(response)
                if not next_page_token:
                    break

                pagination_args.update(next_page_token)

        except Exception as e:
            logger.error(f"Error listing findings for analyzer {parent_id}: {str(e)}")
            yield from []

class CredentialReportStream(BaseIamStream):
    primary_key = "user"
    name = "credential_report"

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            try:
                self.client.generate_credential_report()
            except self.client.exceptions.LimitExceededException:
                pass

            response = self.client.get_credential_report()
            report_csv = response['Content'].decode('utf-8')
            lines = report_csv.splitlines()
            headers = lines[0].split(',')

            for line in lines[1:]:
                values = line.split(',')
                yield dict(zip(headers, values))
        except Exception as e:
            logger.error(f"Error fetching credential report: {str(e)}")
            yield from []

class OrganizationDetailsStream(BaseIamStream):
    primary_key = "Id"
    name = "organization_details"

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            response = self.org_client.describe_organization()
            if 'Organization' in response:
                yield response['Organization']
            else:
                logger.warning("No organization details found in response")
        except Exception as e:
            logger.error(f"Error fetching organization details: {str(e)}")
            yield from []

class ListAccountsStream(BaseIamStream):
    primary_key = "Id"
    name = "list_accounts"
    max_items_per_page = 20

    def next_page_token(self, response: Dict[str, Any]) -> Optional[Mapping[str, Any]]:
        next_token = response.get('NextToken')
        if next_token:
            return {'NextToken': next_token}
        return None

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"MaxResults": self.max_items_per_page}
        if next_page_token:
            params.update(next_page_token)
        return params

    def read_records(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None
    ) -> Iterable[Mapping[str, Any]]:
        try:
            stream_state = stream_state or {}
            pagination_args = self.request_params(
                stream_state=stream_state,
                stream_slice=stream_slice
            )

            while True:
                response = self.org_client.list_accounts(**pagination_args)
                for account in response.get('Accounts', []):
                    if isinstance(account.get('JoinedTimestamp'), datetime):
                        account['JoinedTimestamp'] = account['JoinedTimestamp'].isoformat()
                    yield account

                next_page_token = self.next_page_token(response)
                if not next_page_token:
                    break

                pagination_args.update(next_page_token)
        except Exception as e:
            logger.error(f"Error fetching accounts: {str(e)}")
            yield from []

class IdentityProvidersStream(BaseIamStream):
    primary_key = "Arn"
    name = "identity_providers"

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            providers = self.client.list_saml_providers().get('SAMLProviderList', [])
            yield from providers
        except Exception as e:
            logger.error(f"Error fetching identity providers: {str(e)}")
            yield from []

class RolePoliciesStream(ParentChildIamStream):
    primary_key = "RoleName"
    name = "role_policies"
    parent_stream_class = RolesStream
    parent_id_field = "RoleName"
    max_items_per_page = 100

    def read_records(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None
    ) -> Iterable[Mapping[str, Any]]:
        parent_id = stream_slice.get("parent_id") if stream_slice else None
        if not parent_id:
            return

        try:
            inline_policies = []
            pagination_args = {
                "RoleName": parent_id,
                "MaxItems": self.max_items_per_page
            }

            while True:
                try:
                    response = self.client.list_role_policies(**pagination_args)
                    policy_names = response.get('PolicyNames', [])

                    for policy_name in policy_names:
                        inline_policies.append({
                            "PolicyName": policy_name,
                            "PolicyType": "Inline",
                            "RoleName": parent_id
                        })

                    next_page_token = self.next_page_token(response)
                    if not next_page_token:
                        break

                    pagination_args.update(next_page_token)

                except self.client.exceptions.NoSuchEntityException:
                    logger.warning(f"Role {parent_id} not found")
                    break
                except Exception as e:
                    logger.error(f"Error fetching inline policies for role {parent_id}: {str(e)}")
                    break

            attached_policies = []
            pagination_args = {
                "RoleName": parent_id,
                "MaxItems": self.max_items_per_page
            }

            while True:
                try:
                    response = self.client.list_attached_role_policies(**pagination_args)
                    policies = response.get('AttachedPolicies', [])

                    for policy in policies:
                        policy["PolicyType"] = "Attached"
                        policy["RoleName"] = parent_id
                        attached_policies.append(policy)

                    next_page_token = self.next_page_token(response)
                    if not next_page_token:
                        break

                    pagination_args.update(next_page_token)

                except self.client.exceptions.NoSuchEntityException:
                    break
                except Exception as e:
                    logger.error(f"Error fetching attached policies for role {parent_id}: {str(e)}")
                    break

            yield from inline_policies
            yield from attached_policies

        except Exception as e:
            logger.error(f"Error in read_records: {str(e)}")
            yield from []

class GroupPoliciesStream(ParentChildIamStream):
    primary_key = "GroupName"
    name = "group_policies"
    parent_stream_class = GroupsStream
    parent_id_field = "GroupName"
    max_items_per_page = 100

    def read_records(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None
    ) -> Iterable[Mapping[str, Any]]:
        parent_id = stream_slice.get("parent_id") if stream_slice else None
        if not parent_id:
            return

        try:
            inline_policies = []
            pagination_args = {
                "GroupName": parent_id,
                "MaxItems": self.max_items_per_page
            }

            while True:
                try:
                    response = self.client.list_group_policies(**pagination_args)
                    policy_names = response.get('PolicyNames', [])

                    for policy_name in policy_names:
                        inline_policies.append({
                            "PolicyName": policy_name,
                            "PolicyType": "Inline",
                            "GroupName": parent_id
                        })

                    next_page_token = self.next_page_token(response)
                    if not next_page_token:
                        break

                    pagination_args.update(next_page_token)

                except self.client.exceptions.NoSuchEntityException:
                    logger.warning(f"Group {parent_id} not found")
                    break
                except Exception as e:
                    logger.error(f"Error fetching inline policies for group {parent_id}: {str(e)}")
                    break

            attached_policies = []
            pagination_args = {
                "GroupName": parent_id,
                "MaxItems": self.max_items_per_page
            }

            while True:
                try:
                    response = self.client.list_attached_group_policies(**pagination_args)
                    policies = response.get('AttachedPolicies', [])

                    for policy in policies:
                        policy["PolicyType"] = "Attached"
                        policy["GroupName"] = parent_id
                        attached_policies.append(policy)

                    next_page_token = self.next_page_token(response)
                    if not next_page_token:
                        break

                    pagination_args.update(next_page_token)

                except self.client.exceptions.NoSuchEntityException:
                    break
                except Exception as e:
                    logger.error(f"Error fetching attached policies for group {parent_id}: {str(e)}")
                    break

            yield from inline_policies
            yield from attached_policies

        except Exception as e:
            logger.error(f"Error in read_records: {str(e)}")
            yield from []

class UserPoliciesStream(ParentChildIamStream):
    primary_key = "UserName"
    name = "user_policies"
    parent_stream_class = UsersStream
    parent_id_field = "UserName"
    max_items_per_page = 100

    def read_records(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None
    ) -> Iterable[Mapping[str, Any]]:
        parent_id = stream_slice.get("parent_id") if stream_slice else None
        if not parent_id:
            return

        try:
            inline_policies = []
            pagination_args = {
                "UserName": parent_id,
                "MaxItems": self.max_items_per_page
            }

            while True:
                try:
                    response = self.client.list_user_policies(**pagination_args)
                    policy_names = response.get('PolicyNames', [])

                    for policy_name in policy_names:
                        inline_policies.append({
                            "PolicyName": policy_name,
                            "PolicyType": "Inline",
                            "UserName": parent_id
                        })

                    next_page_token = self.next_page_token(response)
                    if not next_page_token:
                        break

                    pagination_args.update(next_page_token)

                except self.client.exceptions.NoSuchEntityException:
                    logger.warning(f"User {parent_id} not found")
                    break
                except Exception as e:
                    logger.error(f"Error fetching inline policies for user {parent_id}: {str(e)}")
                    break

            attached_policies = []
            pagination_args = {
                "UserName": parent_id,
                "MaxItems": self.max_items_per_page
            }

            while True:
                try:
                    response = self.client.list_attached_user_policies(**pagination_args)
                    policies = response.get('AttachedPolicies', [])

                    for policy in policies:
                        policy["PolicyType"] = "Attached"
                        policy["UserName"] = parent_id
                        attached_policies.append(policy)

                    next_page_token = self.next_page_token(response)
                    if not next_page_token:
                        break

                    pagination_args.update(next_page_token)

                except self.client.exceptions.NoSuchEntityException:
                    break
                except Exception as e:
                    logger.error(f"Error fetching attached policies for user {parent_id}: {str(e)}")
                    break

            yield from inline_policies
            yield from attached_policies

        except Exception as e:
            logger.error(f"Error in read_records: {str(e)}")
            yield from []

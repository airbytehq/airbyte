from typing import Iterable, Mapping, Any

from airbyte_cdk.sources.streams import Stream


class BaseIAMStream(Stream):
    def __init__(self, iam_client, **kwargs):
        super().__init__(**kwargs)
        self.iam = iam_client


class IAMPoliciesStream(BaseIAMStream):
    name = "policy"
    primary_key = "Arn"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "PolicyName": {"type": "string"},
                "PolicyId": {"type": "string"},
                "Arn": {"type": "string"},
                "Path": {"type": "string"},
                "DefaultVersionId": {"type": "string"},
                "AttachmentCount": {"type": "integer"},
                "PermissionsBoundaryUsageCount": {"type": "integer"},
                "IsAttachable": {"type": "boolean"},
                "Description": {"type": ["string", "null"]},
                "CreateDate": {"type": "string", "format": "date-time"},
                "UpdateDate": {"type": "string", "format": "date-time"},
                "Tags": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "Key": {"type": "string"},
                            "Value": {"type": "string"}
                        }
                    }
                }
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        paginator = self.iam.get_paginator("list_policies")
        for page in paginator.paginate(Scope="Local"):
            for policy in page.get("Policies", []):
                yield policy


class IAMRolesStream(BaseIAMStream):
    name = "role"
    primary_key = "Arn"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "RoleName": {"type": "string"},
                "RoleId": {"type": "string"},
                "Arn": {"type": "string"},
                "Path": {"type": "string"},
                "CreateDate": {"type": "string", "format": "date-time"},
                "AssumeRolePolicyDocument": {"type": ["string", "null"]},
                "Description": {"type": ["string", "null"]},
                "MaxSessionDuration": {"type": "integer"},
                "PermissionsBoundary": {
                    "type": ["object", "null"],
                    "properties": {
                        "PermissionsBoundaryType": {"type": "string"},
                        "PermissionsBoundaryArn": {"type": "string"}
                    }
                },
                "Tags": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "Key": {"type": "string"},
                            "Value": {"type": "string"}
                        }
                    }
                },
                "RoleLastUsed": {
                    "type": ["object", "null"],
                    "properties": {
                        "LastUsedDate": {"type": "string", "format": "date-time"},
                        "Region": {"type": "string"}
                    }
                }
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        paginator = self.iam.get_paginator("list_roles")
        for page in paginator.paginate():
            for role in page.get("Roles", []):
                yield role


class IAMUsersStream(BaseIAMStream):
    name = "user"
    primary_key = "Arn"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "UserName": {"type": "string"},
                "UserId": {"type": "string"},
                "Arn": {"type": "string"},
                "Path": {"type": "string"},
                "CreateDate": {"type": "string", "format": "date-time"},
                "PasswordLastUsed": {"type": ["string", "null"], "format": "date-time"},
                "PermissionsBoundary": {
                    "type": ["object", "null"],
                    "properties": {
                        "PermissionsBoundaryType": {"type": "string"},
                        "PermissionsBoundaryArn": {"type": "string"}
                    }
                },
                "Tags": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "Key": {"type": "string"},
                            "Value": {"type": "string"}
                        }
                    }
                }
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        paginator = self.iam.get_paginator("list_users")
        for page in paginator.paginate():
            for user in page.get("Users", []):
                yield user


class IAMGroupsStream(BaseIAMStream):
    name = "group"
    primary_key = "Arn"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "GroupName": {"type": "string"},
                "GroupId": {"type": "string"},
                "Arn": {"type": "string"},
                "Path": {"type": "string"},
                "CreateDate": {"type": "string", "format": "date-time"}
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        paginator = self.iam.get_paginator("list_groups")
        for page in paginator.paginate():
            for group in page.get("Groups", []):
                yield group


class IAMSAMLProvidersStream(BaseIAMStream):
    name = "saml_provider"
    primary_key = "Arn"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "Arn": {"type": "string"},
                "ValidUntil": {"type": ["string", "null"], "format": "date-time"},
                "CreateDate": {"type": ["string", "null"], "format": "date-time"}
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        response = self.iam.list_saml_providers()
        for provider in response.get("SAMLProviderList", []):
            yield provider


class IAMUserInlinePoliciesStream(BaseIAMStream):
    name = "user_inline_policy"
    primary_key = None

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "UserName": {"type": "string"},
                "PolicyName": {"type": "string"},
                "PolicyDocument": {"type": ["object", "string", "null"]}
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        users_paginator = self.iam.get_paginator("list_users")
        for user_page in users_paginator.paginate():
            for user in user_page.get("Users", []):
                user_name = user["UserName"]
                policy_paginator = self.iam.get_paginator("list_user_policies")
                for policy_page in policy_paginator.paginate(UserName=user_name):
                    for policy_name in policy_page.get("PolicyNames", []):
                        policy = self.iam.get_user_policy(UserName=user_name, PolicyName=policy_name)
                        yield {
                            "UserName": user_name,
                            "PolicyName": policy_name,
                            "PolicyDocument": policy.get("PolicyDocument"),
                        }


class IAMRoleInlinePoliciesStream(BaseIAMStream):
    name = "role_inline_policy"
    primary_key = None

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "RoleName": {"type": "string"},
                "PolicyName": {"type": "string"},
                "PolicyDocument": {"type": ["object", "string", "null"]}
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        roles_paginator = self.iam.get_paginator("list_roles")
        for role_page in roles_paginator.paginate():
            for role in role_page.get("Roles", []):
                role_name = role["RoleName"]
                policy_paginator = self.iam.get_paginator("list_role_policies")
                for policy_page in policy_paginator.paginate(RoleName=role_name):
                    for policy_name in policy_page.get("PolicyNames", []):
                        policy = self.iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
                        yield {
                            "RoleName": role_name,
                            "PolicyName": policy_name,
                            "PolicyDocument": policy.get("PolicyDocument"),
                        }

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
                "PolicyVersion": {"type": ["object", "null"]},
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
        
        # Always scan both customer-managed (Local) and AWS managed (AWS) policies
        for scope in ["Local", "AWS"]:
            for page in paginator.paginate(Scope=scope):
                for policy in page.get("Policies", []):
                    # Fetch the latest policy version document
                    try:
                        policy_version = self.iam.get_policy_version(
                            PolicyArn=policy["Arn"],
                            VersionId=policy["DefaultVersionId"]
                        )
                        policy["PolicyVersion"] = policy_version.get("PolicyVersion")
                    except Exception as e:
                        # If we can't fetch the policy version, set it to None
                        policy["PolicyVersion"] = None
                    
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
                "CreateDate": {"type": ["string", "null"], "format": "date-time"},
                "SAMLProviderUUID": {"type": ["string", "null"]},
                "SAMLMetadataDocument": {"type": ["string", "null"]},
                "AssertionEncryptionMode": {"type": ["string", "null"]},
                "Tags": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "Key": {"type": "string"},
                            "Value": {"type": "string"}
                        }
                    }
                },
                "PrivateKeyList": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "KeyId": {"type": "string"},
                            "Timestamp": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        # First, list all SAML providers
        response = self.iam.list_saml_providers()
        for provider in response.get("SAMLProviderList", []):
            # Get detailed information for each provider
            try:
                detailed_response = self.iam.get_saml_provider(
                    SAMLProviderArn=provider["Arn"]
                )
                
                # Merge the basic info from list_saml_providers with detailed info from get_saml_provider
                detailed_provider = {
                    "Arn": provider["Arn"],
                    "ValidUntil": provider.get("ValidUntil"),
                    "CreateDate": provider.get("CreateDate"),
                    "SAMLProviderUUID": detailed_response.get("SAMLProviderUUID"),
                    "SAMLMetadataDocument": detailed_response.get("SAMLMetadataDocument"),
                    "AssertionEncryptionMode": detailed_response.get("AssertionEncryptionMode"),
                    "Tags": detailed_response.get("Tags"),
                    "PrivateKeyList": detailed_response.get("PrivateKeyList")
                }
                
                yield detailed_provider
            except Exception as e:
                # If we can't fetch detailed info, return the basic info from list_saml_providers
                # This ensures backward compatibility and robustness
                provider_copy = provider.copy()
                provider_copy.update({
                    "SAMLProviderUUID": None,
                    "SAMLMetadataDocument": None,
                    "AssertionEncryptionMode": None,
                    "Tags": None,
                    "PrivateKeyList": None
                })
                yield provider_copy


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
                            "Arn": f"user_arn/{policy_name}",
                            "UserArn": user["Arn"],
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
                "Arn": {"type": "string"},
                "RoleArn": {"type": "string"},
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
                role_arn = role["Arn"]
                policy_paginator = self.iam.get_paginator("list_role_policies")
                for policy_page in policy_paginator.paginate(RoleName=role_name):
                    for policy_name in policy_page.get("PolicyNames", []):
                        policy = self.iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
                        yield {
                            "Arn": f"role_arn/{policy_name}",
                            "RoleArn": role_arn,
                            "RoleName": role_name,
                            "PolicyName": policy_name,
                            "PolicyDocument": policy.get("PolicyDocument"),
                        }


class IAMGroupInlinePoliciesStream(BaseIAMStream):
    name = "group_inline_policy"
    primary_key = None

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "Arn": {"type": "string"},
                "GroupArn": {"type": "string"},
                "GroupName": {"type": "string"},
                "PolicyName": {"type": "string"},
                "PolicyDocument": {"type": ["object", "string", "null"]}
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        groups_paginator = self.iam.get_paginator("list_groups")
        for group_page in groups_paginator.paginate():
            for group in group_page.get("Groups", []):
                group_name = group["GroupName"]
                group_arn = group["Arn"]
                policy_paginator = self.iam.get_paginator("list_group_policies")
                for policy_page in policy_paginator.paginate(GroupName=group_name):
                    for policy_name in policy_page.get("PolicyNames", []):
                        policy = self.iam.get_group_policy(GroupName=group_name, PolicyName=policy_name)
                        yield {
                            "Arn": f"group_arn/{policy_name}",
                            "GroupArn": group_arn,
                            "GroupName": group_name,
                            "PolicyName": policy_name,
                            "PolicyDocument": policy.get("PolicyDocument"),
                        }


class IAMInlinePoliciesStream(BaseIAMStream):
    name = "inline_policy"
    primary_key = None

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "Arn": {"type": "string"},
                "IamIdentityArn": {"type": "string"},
                "PolicyDocument": {"type": ["object", "null"]},
                "PolicyName": {"type": "string"},
                "RoleName": {"type": ["string", "null"]}
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        # Get user inline policies
        users_paginator = self.iam.get_paginator("list_users")
        for user_page in users_paginator.paginate():
            for user in user_page.get("Users", []):
                user_name = user["UserName"]
                user_arn = user["Arn"]
                policy_paginator = self.iam.get_paginator("list_user_policies")
                for policy_page in policy_paginator.paginate(UserName=user_name):
                    for policy_name in policy_page.get("PolicyNames", []):
                        policy = self.iam.get_user_policy(UserName=user_name, PolicyName=policy_name)
                        yield {
                            "Arn": f"{user_arn}/{policy_name}",
                            "IamIdentityArn": user_arn,
                            "PolicyDocument": policy.get("PolicyDocument"),
                            "PolicyName": policy_name,
                            "UserName": user_name
                        }

        # Get role inline policies
        roles_paginator = self.iam.get_paginator("list_roles")
        for role_page in roles_paginator.paginate():
            for role in role_page.get("Roles", []):
                role_name = role["RoleName"]
                role_arn = role["Arn"]
                policy_paginator = self.iam.get_paginator("list_role_policies")
                for policy_page in policy_paginator.paginate(RoleName=role_name):
                    for policy_name in policy_page.get("PolicyNames", []):
                        policy = self.iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
                        yield {
                            "Arn": f"{role_arn}/{policy_name}",
                            "IamIdentityArn": role_arn,
                            "PolicyDocument": policy.get("PolicyDocument"),
                            "PolicyName": policy_name,
                            "RoleName": role_name,
                            "UserName": None,
                            "GroupName": None
                        }

        # Get group inline policies
        groups_paginator = self.iam.get_paginator("list_groups")
        for group_page in groups_paginator.paginate():
            for group in group_page.get("Groups", []):
                group_name = group["GroupName"]
                group_arn = group["Arn"]
                policy_paginator = self.iam.get_paginator("list_group_policies")
                for policy_page in policy_paginator.paginate(GroupName=group_name):
                    for policy_name in policy_page.get("PolicyNames", []):
                        policy = self.iam.get_group_policy(GroupName=group_name, PolicyName=policy_name)
                        yield {
                            "Arn": f"{group_arn}/{policy_name}",
                            "IamIdentityArn": group_arn,
                            "PolicyDocument": policy.get("PolicyDocument"),
                            "PolicyName": policy_name,
                            "GroupName": group_name,
                            "UserName": None,
                            "RoleName": None
                        }


class IAMUserPolicyBindingsStream(BaseIAMStream):
    name = "user_policy_binding"
    primary_key = None

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "UserArn": {"type": "string"},
                "UserName": {"type": "string"},
                "PolicyArn": {"type": "string"},
                "PolicyName": {"type": "string"}
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        users_paginator = self.iam.get_paginator("list_users")
        for user_page in users_paginator.paginate():
            for user in user_page.get("Users", []):
                user_name = user["UserName"]
                user_arn = user["Arn"]
                policy_paginator = self.iam.get_paginator("list_attached_user_policies")
                for policy_page in policy_paginator.paginate(UserName=user_name):
                    for policy in policy_page.get("AttachedPolicies", []):
                        yield {
                            "UserArn": user_arn,
                            "UserName": user_name,
                            "PolicyArn": policy["PolicyArn"],
                            "PolicyName": policy["PolicyName"]
                        }


class IAMRolePolicyBindingsStream(BaseIAMStream):
    name = "role_policy_binding"
    primary_key = None

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "RoleArn": {"type": "string"},
                "RoleName": {"type": "string"},
                "PolicyArn": {"type": "string"},
                "PolicyName": {"type": "string"}
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        roles_paginator = self.iam.get_paginator("list_roles")
        for role_page in roles_paginator.paginate():
            for role in role_page.get("Roles", []):
                role_name = role["RoleName"]
                role_arn = role["Arn"]
                policy_paginator = self.iam.get_paginator("list_attached_role_policies")
                for policy_page in policy_paginator.paginate(RoleName=role_name):
                    for policy in policy_page.get("AttachedPolicies", []):
                        yield {
                            "RoleArn": role_arn,
                            "RoleName": role_name,
                            "PolicyArn": policy["PolicyArn"],
                            "PolicyName": policy["PolicyName"]
                        }


class IAMGroupPolicyBindingsStream(BaseIAMStream):
    name = "group_policy_binding"
    primary_key = None

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "GroupArn": {"type": "string"},
                "GroupName": {"type": "string"},
                "PolicyArn": {"type": "string"},
                "PolicyName": {"type": "string"}
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        groups_paginator = self.iam.get_paginator("list_groups")
        for group_page in groups_paginator.paginate():
            for group in group_page.get("Groups", []):
                group_name = group["GroupName"]
                group_arn = group["Arn"]
                policy_paginator = self.iam.get_paginator("list_attached_group_policies")
                for policy_page in policy_paginator.paginate(GroupName=group_name):
                    for policy in policy_page.get("AttachedPolicies", []):
                        yield {
                            "GroupArn": group_arn,
                            "GroupName": group_name,
                            "PolicyArn": policy["PolicyArn"],
                            "PolicyName": policy["PolicyName"]
                        }

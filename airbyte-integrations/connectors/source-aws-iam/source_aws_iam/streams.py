import json
import logging
import os
import subprocess
from datetime import datetime
from subprocess import CalledProcessError
from typing import Any, Iterable, Mapping

import boto3
from airbyte_cdk.sources.streams import Stream
from botocore.session import get_session


def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime(item) for item in obj]
    else:
        return obj


class BaseIAMStream(Stream):
    def __init__(self, iam_client, **kwargs):
        super().__init__(**kwargs)
        self.iam = iam_client


class IAMPoliciesStream(BaseIAMStream):
    name = "iam_policy"
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
                    
                    yield serialize_datetime(policy)


class IAMRolesStream(BaseIAMStream):
    name = "iam_role"
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
                yield serialize_datetime(role)


class IAMUsersStream(BaseIAMStream):
    name = "iam_user"
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
                yield serialize_datetime(user)


class IAMGroupsStream(BaseIAMStream):
    name = "iam_group"
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
                yield serialize_datetime(group)


class IAMSAMLProvidersStream(BaseIAMStream):
    name = "iam_saml_provider"
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
                
                yield serialize_datetime(detailed_provider)
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
                yield serialize_datetime(provider_copy)


class IAMUserInlinePoliciesStream(BaseIAMStream):
    name = "iam_user_inline_policy"
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
                            "Arn": f"{user['Arn']}/{policy_name}",
                            "UserArn": user["Arn"],
                            "UserName": user_name,
                            "PolicyName": policy_name,
                            "PolicyDocument": policy.get("PolicyDocument"),
                        }


class IAMRoleInlinePoliciesStream(BaseIAMStream):
    name = "iam_role_inline_policy"
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
                            "Arn": f"{role_arn}/{policy_name}",
                            "RoleArn": role_arn,
                            "RoleName": role_name,
                            "PolicyName": policy_name,
                            "PolicyDocument": policy.get("PolicyDocument"),
                        }


class IAMGroupInlinePoliciesStream(BaseIAMStream):
    name = "iam_group_inline_policy"
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
                            "Arn": f"{group_arn}/{policy_name}",
                            "GroupArn": group_arn,
                            "GroupName": group_name,
                            "PolicyName": policy_name,
                            "PolicyDocument": policy.get("PolicyDocument"),
                        }


class IAMInlinePoliciesStream(BaseIAMStream):
    name = "iam_inline_policy"
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
    name = "iam_user_policy_binding"
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
    name = "iam_role_policy_binding"
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
    name = "iam_group_policy_binding"
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


# Stream: link IAM groups and IAM users (group membership)
class IAMGroupUserMembershipStream(BaseIAMStream):
    """Stream returning which users belong to which IAM groups."""
    name = "iam_group_user_membership"
    primary_key = None

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "GroupName": {"type": "string"},
                "GroupArn": {"type": "string"},
                "UserName": {"type": "string"},
                "UserArn": {"type": "string"}
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        # List all groups
        groups_paginator = self.iam.get_paginator("list_groups")
        for page in groups_paginator.paginate():
            for group in page.get("Groups", []):
                group_name = group.get("GroupName")
                group_arn = group.get("Arn")
                # Get users in this group, handling pagination
                marker = None
                while True:
                    params = {"GroupName": group_name}
                    if marker:
                        params["Marker"] = marker
                    response = self.iam.get_group(**params)
                    for user in response.get("Users", []):
                        yield serialize_datetime({
                            "GroupName": group_name,
                            "GroupArn": group_arn,
                            "UserName": user.get("UserName"),
                            "UserArn": user.get("Arn")
                        })
                    if response.get("IsTruncated"):
                        marker = response.get("Marker")
                    else:
                        break


# Streams for AWS Identity Center via Identity Store
class BaseIdentityCenterStream(Stream):
    """Base class for AWS Identity Center streams, sharing assumed-role credentials."""
    def __init__(self, identitystore_client, sso_admin_client, **kwargs):
        super().__init__(**kwargs)
        self.identitystore = identitystore_client
        self.sso_admin = sso_admin_client


# Stream: list Identity Center instances (parent for other identity streams)
class IdentityCenterInstanceStream(BaseIdentityCenterStream):
    name = "identity_center_instance"
    primary_key = "InstanceArn"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "InstanceArn": {"type": "string"},
                "IdentityStoreId": {"type": "string"}
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            resp = self.sso_admin.list_instances()
            for inst in resp.get("Instances", []):
                yield serialize_datetime(inst)
        except Exception as e:
            # If we don't have permissions to list instances, log and return empty
            logging.warning(f"Cannot list Identity Center instances: {str(e)}")
            return  


class IdentityCenterUserStream(BaseIdentityCenterStream):
    name = "identity_center_user"
    primary_key = "UserId"

    def stream_slices(self, **kwargs):
        # Slice by each Identity Center instance
        try:
            for inst in IdentityCenterInstanceStream(self.identitystore,self.sso_admin).read_records():
                yield inst
        except Exception as e:
            logging.warning(f"Cannot access Identity Center instances for users: {str(e)}")
            return

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "UserId": {"type": "string"},
                "UserName": {"type": ["string", "null"]},
                "DisplayName": {"type": ["string", "null"]},
                "ExternalIds": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "Issuer": {"type": "string"},
                            "Id": {"type": "string"}
                        }
                    }
                },
                "Name": {
                    "type": ["object", "null"],
                    "properties": {
                        "FamilyName": {"type": ["string", "null"]},
                        "GivenName": {"type": ["string", "null"]}
                    }
                },
                "Emails": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "Value": {"type": ["string", "null"]},
                            "Type": {"type": ["string", "null"]},
                            "Primary": {"type": "boolean"}
                        }
                    }
                },
                "PhoneNumbers": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "Value": {"type": ["string", "null"]},
                            "Type": {"type": ["string", "null"]},
                            "Primary": {"type": "boolean"}
                        }
                    }
                },
                "Locale": {"type": ["string", "null"]},
                "IdentityStoreId": {"type": "string"}
            }
        }

    def read_records(self, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Mapping[str, Any]]:
        identity_store_id = stream_slice.get("IdentityStoreId")
        try:
            paginator = self.identitystore.get_paginator("list_users")
            for page in paginator.paginate(IdentityStoreId=identity_store_id):
                for user in page.get("Users", []):
                    yield serialize_datetime(user)
        except Exception as e:
            logging.warning(f"Cannot list users for identity store {identity_store_id}: {str(e)}")
            return


class IdentityCenterGroupStream(BaseIdentityCenterStream):
    name = "identity_center_group"
    primary_key = "GroupId"

    def stream_slices(self, **kwargs):
        try:
            for inst in IdentityCenterInstanceStream(self.identitystore,self.sso_admin).read_records():
                yield inst
        except Exception as e:
            logging.warning(f"Cannot access Identity Center instances for groups: {str(e)}")
            return

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "GroupId": {"type": "string"},
                "DisplayName": {"type": "string"},
                "Description": {"type": ["string", "null"]},
                "ExternalIds": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "Issuer": {"type": "string"},
                            "Id": {"type": "string"}
                        }
                    }
                },
                "Meta": {
                    "type": ["object", "null"],
                    "properties": {
                        "CreatedBy": {"type": ["string", "null"]},
                        "CreatedDate": {"type": ["string", "null"], "format": "date-time"},
                        "LastModifiedBy": {"type": ["string", "null"]},
                        "LastModifiedDate": {"type": ["string", "null"], "format": "date-time"},
                        "ResourceType": {"type": ["string", "null"]},
                        "Version": {"type": ["string", "null"]}
                    }
                }
            }
        }

    def read_records(self, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Mapping[str, Any]]:
        identity_store_id = stream_slice.get("IdentityStoreId")
        try:
            paginator = self.identitystore.get_paginator("list_groups")
            for page in paginator.paginate(IdentityStoreId=identity_store_id):
                for group in page.get("Groups", []):
                    yield serialize_datetime(group)
        except Exception as e:
            logging.warning(f"Cannot list groups for identity store {identity_store_id}: {str(e)}")
            return


class IdentityCenterGroupMembershipStream(BaseIdentityCenterStream):
    name = "identity_center_group_membership"
    primary_key = None

    def stream_slices(self, **kwargs):
        try:
            for inst in IdentityCenterInstanceStream(self.identitystore,self.sso_admin).read_records():
                yield inst
        except Exception as e:
            logging.warning(f"Cannot access Identity Center instances for group memberships: {str(e)}")
            return

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "GroupId": {"type": "string"},
                "UserId": {"type": "string"}
            }
        }

    def read_records(self, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Mapping[str, Any]]:
        identity_store_id = stream_slice.get("IdentityStoreId")
        try:
            # First, list all groups for this store
            groups = []
            pg = self.identitystore.get_paginator("list_groups")
            for page in pg.paginate(IdentityStoreId=identity_store_id):
                groups.extend(page.get("Groups", []))
            # For each group, list memberships
            mp = self.identitystore.get_paginator("list_group_memberships")
            for group in groups:
                gid = group.get("GroupId")
                try:
                    for page in mp.paginate(IdentityStoreId=identity_store_id, GroupId=gid):
                        for membership in page.get("GroupMemberships", []):
                            uid = membership.get("MemberId", {}).get("UserId")
                            yield serialize_datetime({"GroupId": gid, "UserId": uid})
                except Exception as e:
                    logging.warning(f"Cannot list memberships for group {gid}: {str(e)}")
                    continue
        except Exception as e:
            logging.warning(f"Cannot list group memberships for identity store {identity_store_id}: {str(e)}")
            return

# Add these new streams after the existing Identity Center streams, and remove the other SSO Admin streams

class IdentityCenterUserToRoleStream(BaseIdentityCenterStream):
    """Stream that maps Identity Center users directly to the IAM role ARNs they can assume."""
    name = "identity_center_user_to_role"
    primary_key = None

    def stream_slices(self, **kwargs):
        # Slice by each Identity Center instance
        try:
            for inst in IdentityCenterInstanceStream(self.identitystore, self.sso_admin).read_records():
                yield inst
        except Exception as e:
            logging.warning(f"Cannot access Identity Center instances for user-to-role mapping: {str(e)}")
            return

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "UserId": {"type": "string"},
                "UserName": {"type": ["string", "null"]},
                "DisplayName": {"type": ["string", "null"]},
                "RoleArn": {"type": "string"},
                "RoleName": {"type": "string"},
                "AccountId": {"type": "string"},
                "PermissionSetArn": {"type": "string"},
                "PermissionSetName": {"type": ["string", "null"]},
                "AssignmentType": {"type": "string", "enum": ["DIRECT"]}
            }
        }

    def read_records(self, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Mapping[str, Any]]:
        instance_arn = stream_slice.get("InstanceArn")
        identity_store_id = stream_slice.get("IdentityStoreId")
        
        if not instance_arn or not identity_store_id:
            logging.warning("Missing InstanceArn or IdentityStoreId in stream slice")
            return

        try:
            # Get all users first
            user_paginator = self.identitystore.get_paginator("list_users")
            for user_page in user_paginator.paginate(IdentityStoreId=identity_store_id):
                for user in user_page.get("Users", []):
                    user_id = user.get("UserId")
                    user_name = user.get("UserName")
                    display_name = user.get("DisplayName")
                    
                    if not user_id:
                        continue
                    
                    # collect assignments inherited via groups for this user
                    inherited = set()
                    try:
                        group_mem_paginator = self.identitystore.get_paginator("list_group_memberships_for_member")
                        for mem_page in group_mem_paginator.paginate(
                            IdentityStoreId=identity_store_id,
                            MemberId={"UserId": user_id}
                        ):
                            for mem in mem_page.get("GroupMemberships", []):
                                g_id = mem.get("GroupId")
                                if not g_id:
                                    continue
                                grp_assign_paginator = self.sso_admin.get_paginator("list_account_assignments_for_principal")
                                for grp_page in grp_assign_paginator.paginate(
                                    InstanceArn=instance_arn,
                                    PrincipalId=g_id,
                                    PrincipalType="GROUP"
                                ):
                                    for ga in grp_page.get("AccountAssignments", []):
                                        inherited.add((ga.get("AccountId"), ga.get("PermissionSetArn")))
                    except Exception:
                        pass

                    # Get direct assignments for this user
                    try:
                        assignment_paginator = self.sso_admin.get_paginator("list_account_assignments_for_principal")
                        for assignment_page in assignment_paginator.paginate(
                            InstanceArn=instance_arn,
                            PrincipalId=user_id,
                            PrincipalType="USER"
                        ):
                            for assignment in assignment_page.get("AccountAssignments", []):
                                account_id = assignment.get("AccountId")
                                permission_set_arn = assignment.get("PermissionSetArn")
                                # skip if inherited via a group
                                if (account_id, permission_set_arn) in inherited:
                                    continue
                                if account_id and permission_set_arn:
                                    # Fetch permission set name
                                    permission_set_name = None
                                    try:
                                        ps_resp = self.sso_admin.describe_permission_set(
                                            InstanceArn=instance_arn,
                                            PermissionSetArn=permission_set_arn
                                        )
                                        permission_set_name = ps_resp.get("PermissionSet", {}).get("Name")
                                    except Exception:
                                        pass
                                    # Build role ARN
                                    ps_id = permission_set_arn.split('/')[-1]
                                    if ps_id.startswith("ps-"):
                                        ps_id = ps_id[3:]
                                    role_name = f"AWSReservedSSO_{permission_set_name}_{ps_id}" if permission_set_name else f"AWSReservedSSO_{ps_id}"
                                    role_arn = f"arn:aws:iam::{account_id}:role/aws-reserved/sso.amazonaws.com/{role_name}"
                                    yield serialize_datetime({
                                        "UserId": user_id,
                                        "UserName": user_name,
                                        "DisplayName": display_name,
                                        "RoleArn": role_arn,
                                        "RoleName": role_name,
                                        "AccountId": account_id,
                                        "PermissionSetArn": permission_set_arn,
                                        "PermissionSetName": permission_set_name,
                                        "AssignmentType": "DIRECT"
                                    })
                    except Exception as e:
                        logging.warning(f"Cannot list direct assignments for user {user_id}: {str(e)}")
                        
        except Exception as e:
            logging.warning(f"Cannot list users for identity store {identity_store_id}: {str(e)}")
            return


class IdentityCenterGroupToRoleStream(BaseIdentityCenterStream):
    """Stream that maps Identity Center groups directly to the IAM role ARNs they can assume."""
    name = "identity_center_group_to_role"
    primary_key = None

    def stream_slices(self, **kwargs):
        # Slice by each Identity Center instance
        try:
            for inst in IdentityCenterInstanceStream(self.identitystore, self.sso_admin).read_records():
                yield inst
        except Exception as e:
            logging.warning(f"Cannot access Identity Center instances for group-to-role mapping: {str(e)}")
            return

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "GroupId": {"type": "string"},
                "GroupName": {"type": ["string", "null"]},
                "Description": {"type": ["string", "null"]},
                "RoleArn": {"type": "string"},
                "RoleName": {"type": "string"},
                "AccountId": {"type": "string"},
                "PermissionSetArn": {"type": "string"},
                "PermissionSetName": {"type": ["string", "null"]}
            }
        }

    def read_records(self, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Mapping[str, Any]]:
        instance_arn = stream_slice.get("InstanceArn")
        identity_store_id = stream_slice.get("IdentityStoreId")
        
        if not instance_arn or not identity_store_id:
            logging.warning("Missing InstanceArn or IdentityStoreId in stream slice")
            return

        try:
            # Get all groups first
            group_paginator = self.identitystore.get_paginator("list_groups")
            for group_page in group_paginator.paginate(IdentityStoreId=identity_store_id):
                for group in group_page.get("Groups", []):
                    group_id = group.get("GroupId")
                    group_name = group.get("DisplayName")
                    description = group.get("Description")
                    
                    if not group_id:
                        continue
                    
                    # Get assignments for this group
                    try:
                        assignment_paginator = self.sso_admin.get_paginator("list_account_assignments_for_principal")
                        for assignment_page in assignment_paginator.paginate(
                            InstanceArn=instance_arn,
                            PrincipalId=group_id,
                            PrincipalType="GROUP"
                        ):
                            for assignment in assignment_page.get("AccountAssignments", []):
                                account_id = assignment.get("AccountId")
                                permission_set_arn = assignment.get("PermissionSetArn")
                                
                                if account_id and permission_set_arn:
                                    # Get permission set details to get the name
                                    permission_set_name = None
                                    try:
                                        ps_response = self.sso_admin.describe_permission_set(
                                            InstanceArn=instance_arn,
                                            PermissionSetArn=permission_set_arn
                                        )
                                        permission_set_name = ps_response.get("PermissionSet", {}).get("Name")
                                    except Exception as e:
                                        logging.warning(f"Cannot get permission set details for {permission_set_arn}: {str(e)}")
                                    
                                    # Construct the role ARN (legacy behavior)
                                    permission_set_id = permission_set_arn.split('/')[-1]
                                    if permission_set_id.startswith("ps-"):
                                        permission_set_id = permission_set_id[3:]
                                    role_name = f"AWSReservedSSO_{permission_set_name}_{permission_set_id}" if permission_set_name else f"AWSReservedSSO_{permission_set_id}"
                                    role_arn = f"arn:aws:iam::{account_id}:role/aws-reserved/sso.amazonaws.com/{role_name}"

                                    yield serialize_datetime({
                                        "GroupId": group_id,
                                        "GroupName": group_name,
                                        "Description": description,
                                        "RoleArn": role_arn,
                                        "RoleName": role_name,
                                        "AccountId": account_id,
                                        "PermissionSetArn": permission_set_arn,
                                        "PermissionSetName": permission_set_name
                                    })
                    except Exception as e:
                        logging.warning(f"Cannot list assignments for group {group_id}: {str(e)}")
                        
        except Exception as e:
            logging.warning(f"Cannot list groups for identity store {identity_store_id}: {str(e)}")
            return
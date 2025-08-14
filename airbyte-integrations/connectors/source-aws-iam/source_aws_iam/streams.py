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


class IAMAccessKeysStream(BaseIAMStream):
    name = "iam_access_key"
    primary_key = "AccessKeyId"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "AccessKeyId": {"type": "string"},
                "UserName": {"type": "string"},
                "UserArn": {"type": "string"},
                "Status": {"type": "string", "enum": ["Active", "Inactive"]},
                "CreateDate": {"type": "string", "format": "date-time"},
                "LastUsedDate": {"type": ["string", "null"], "format": "date-time"},
                "LastUsedRegion": {"type": ["string", "null"]},
                "LastUsedServiceName": {"type": ["string", "null"]}
            }
        }

    def stream_slices(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Create slices for each user to enable concurrent processing.
        Each slice contains a user to process for access keys.
        """
        users_paginator = self.iam.get_paginator("list_users")
        for user_page in users_paginator.paginate():
            for user in user_page.get("Users", []):
                yield {
                    "user_name": user["UserName"],
                    "user_arn": user["Arn"]
                }

    def read_records(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Process access keys for a single user (from the stream slice).
        This allows concurrent processing of different users.
        """
        if not stream_slice:
            # Fallback for backwards compatibility - shouldn't happen in concurrent mode
            logging.warning("No stream slice provided, falling back to sequential processing")
            yield from self._read_all_users_sequentially()
            return
            
        user_name = stream_slice["user_name"]
        user_arn = stream_slice["user_arn"]
        
        # Get access keys for this specific user
        try:
            access_keys_paginator = self.iam.get_paginator("list_access_keys")
            for keys_page in access_keys_paginator.paginate(UserName=user_name):
                for access_key in keys_page.get("AccessKeyMetadata", []):
                    access_key_data = {
                        "AccessKeyId": access_key.get("AccessKeyId"),
                        "UserName": user_name,
                        "UserArn": user_arn,
                        "Status": access_key.get("Status"),
                        "CreateDate": access_key.get("CreateDate"),
                        "LastUsedDate": None,
                        "LastUsedRegion": None,
                        "LastUsedServiceName": None
                    }
                    
                    # Try to get last used information for the access key
                    try:
                        last_used_response = self.iam.get_access_key_last_used(
                            AccessKeyId=access_key.get("AccessKeyId")
                        )
                        last_used = last_used_response.get("AccessKeyLastUsed", {})
                        access_key_data.update({
                            "LastUsedDate": last_used.get("LastUsedDate"),
                            "LastUsedRegion": last_used.get("Region"),
                            "LastUsedServiceName": last_used.get("ServiceName")
                        })
                    except Exception as e:
                        # If we can't get last used info, continue with None values
                        logging.warning(f"Cannot get last used info for access key {access_key.get('AccessKeyId')}: {str(e)}")
                    
                    yield serialize_datetime(access_key_data)
                    
        except Exception as e:
            # If we can't list access keys for this user, log and continue
            logging.warning(f"Cannot list access keys for user {user_name}: {str(e)}")
            return

    def _read_all_users_sequentially(self) -> Iterable[Mapping[str, Any]]:
        """
        Fallback method for sequential processing when no stream slices are provided.
        This maintains backwards compatibility.
        """
        users_paginator = self.iam.get_paginator("list_users")
        for user_page in users_paginator.paginate():
            for user in user_page.get("Users", []):
                user_name = user["UserName"]
                user_arn = user["Arn"]
                
                # Get access keys for this user
                try:
                    access_keys_paginator = self.iam.get_paginator("list_access_keys")
                    for keys_page in access_keys_paginator.paginate(UserName=user_name):
                        for access_key in keys_page.get("AccessKeyMetadata", []):
                            access_key_data = {
                                "AccessKeyId": access_key.get("AccessKeyId"),
                                "UserName": user_name,
                                "UserArn": user_arn,
                                "Status": access_key.get("Status"),
                                "CreateDate": access_key.get("CreateDate"),
                                "LastUsedDate": None,
                                "LastUsedRegion": None,
                                "LastUsedServiceName": None
                            }
                            
                            # Try to get last used information for the access key
                            try:
                                last_used_response = self.iam.get_access_key_last_used(
                                    AccessKeyId=access_key.get("AccessKeyId")
                                )
                                last_used = last_used_response.get("AccessKeyLastUsed", {})
                                access_key_data.update({
                                    "LastUsedDate": last_used.get("LastUsedDate"),
                                    "LastUsedRegion": last_used.get("Region"),
                                    "LastUsedServiceName": last_used.get("ServiceName")
                                })
                            except Exception as e:
                                # If we can't get last used info, continue with None values
                                logging.warning(f"Cannot get last used info for access key {access_key.get('AccessKeyId')}: {str(e)}")
                            
                            yield serialize_datetime(access_key_data)
                            
                except Exception as e:
                    # If we can't list access keys for this user, log and continue
                    logging.warning(f"Cannot list access keys for user {user_name}: {str(e)}")
                    continue


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


# Base class for AWS Secrets Manager streams
class BaseSecretsManagerStream(Stream):
    """Base class for AWS Secrets Manager streams."""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._region_clients = {}

    def _get_secretsmanager_client_for_region(self, region: str):
        """Get or create a Secrets Manager client for a specific region."""
        if region not in self._region_clients:
            logging.info(f"Creating Secrets Manager client for region {region}")
            role_arn = self.config.get("role_arn")
            external_id = self.config.get("external_id")
            
            if role_arn:
                logging.info(f"Using assume role {role_arn} for region {region}")
                self._region_clients[region] = self._get_client_with_assume_role(
                    aws_service="secretsmanager", 
                    role_arn=role_arn, 
                    external_id=external_id, 
                    region=region
                )
            else:
                logging.info(f"Using default credentials for region {region}")
                self._region_clients[region] = boto3.client("secretsmanager", region_name=region)
            
            logging.info(f"Successfully created Secrets Manager client for region {region}")
        
        return self._region_clients[region]

    def _get_client_with_assume_role(self, aws_service: str, role_arn: str, external_id: str = None, region: str = None):
        """Create a client using assume role credentials for a specific region."""
        
        try:
            sts_client = boto3.client("sts")
            assume_role_kwargs = {
                "RoleArn": role_arn,
                "RoleSessionName": f"airbyte-secretsmanager-{region}"
            }
            if external_id:
                assume_role_kwargs["ExternalId"] = external_id
                
            credentials = sts_client.assume_role(**assume_role_kwargs)["Credentials"]
            
            # Create a new session with the assumed role credentials
            session = boto3.Session(
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
                region_name=region
            )
            
            return session.client(aws_service)
            
        except Exception as e:
            logging.error(f"Failed to assume role {role_arn} for region {region}: {str(e)}")
            raise

    def _get_all_aws_regions(self):
        """Get list of AWS regions that support Secrets Manager."""
        # Only include commonly available regions that support Secrets Manager
        # Excluding opt-in regions that may cause authentication issues
        return [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1', 'eu-north-1',
            'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2', 'ap-south-1',
            'ca-central-1', 'sa-east-1'
        ]


class SecretsManagerSecretsStream(BaseSecretsManagerStream):
    """Stream to read AWS Secrets Manager secrets metadata (excludes secret values for security)."""
    name = "secrets_manager_secret"
    primary_key = "ARN"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "ARN": {"type": "string"},
                "Name": {"type": "string"},
                "Description": {"type": ["string", "null"]},
                "KmsKeyId": {"type": ["string", "null"]},
                "RotationEnabled": {"type": "boolean"},
                "RotationLambdaARN": {"type": ["string", "null"]},
                "RotationRules": {
                    "type": ["object", "null"],
                    "properties": {
                        "AutomaticallyAfterDays": {"type": ["integer", "null"]}
                    }
                },
                "LastRotatedDate": {"type": ["string", "null"], "format": "date-time"},
                "LastChangedDate": {"type": ["string", "null"], "format": "date-time"},
                "LastAccessedDate": {"type": ["string", "null"], "format": "date-time"},
                "DeletedDate": {"type": ["string", "null"], "format": "date-time"},
                "NextRotationDate": {"type": ["string", "null"], "format": "date-time"},
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
                "SecretVersionsToStages": {
                    "type": ["object", "null"],
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "OwningService": {"type": ["string", "null"]},
                "CreatedDate": {"type": ["string", "null"], "format": "date-time"},
                "PrimaryRegion": {"type": ["string", "null"]},
                "ReplicationStatus": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "Region": {"type": "string"},
                            "KmsKeyId": {"type": ["string", "null"]},
                            "Status": {"type": "string"},
                            "StatusMessage": {"type": ["string", "null"]},
                            "LastAccessedDate": {"type": ["string", "null"], "format": "date-time"}
                        }
                    }
                },
                "Region": {"type": "string"}
            }
        }

    def stream_slices(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Create slices for each region and secret combination to enable concurrent processing.
        Each slice contains a region, secret ARN and secret name to process.
        """
        slice_count = 0
        regions_processed = 0
        
        for region in self._get_all_aws_regions():
            logging.info(f"Checking region {region} for secrets...")
            client = self._get_secretsmanager_client_for_region(region)
            paginator = client.get_paginator("list_secrets")
            
            secrets_in_region = 0
            for page in paginator.paginate():
                for secret in page.get("SecretList", []):
                    secrets_in_region += 1
                    slice_count += 1
                    yield {
                        "region": region,
                        "secret_arn": secret.get("ARN"),
                        "secret_name": secret.get("Name")
                    }
            
            if secrets_in_region > 0:
                logging.info(f"Found {secrets_in_region} secrets in region {region}")
            else:
                logging.info(f"No secrets found in region {region}")
            regions_processed += 1
        
        logging.info(f"Processed {regions_processed} regions, generated {slice_count} slices")

    def read_records(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Process metadata for a single secret (from the stream slice).
        This allows concurrent processing of different secrets across regions.
        """
        if not stream_slice:
            # Fallback for backwards compatibility - shouldn't happen in concurrent mode
            logging.warning("No stream slice provided, falling back to sequential processing")
            yield from self._read_all_secrets_sequentially()
            return

        region = stream_slice["region"]
        secret_arn = stream_slice["secret_arn"]
        secret_name = stream_slice["secret_name"]

        logging.info(f"Processing secret {secret_name} in region {region}")

        client = self._get_secretsmanager_client_for_region(region)
        # Get detailed metadata for this specific secret
        response = client.describe_secret(SecretId=secret_arn)
        
        # Remove sensitive data - we only want metadata
        secret_metadata = response.copy()
        # Remove any potential secret value fields (defensive programming)
        secret_metadata.pop("SecretString", None)
        secret_metadata.pop("SecretBinary", None)
        
        # Add region information to the metadata
        secret_metadata["Region"] = region
        
        logging.info(f"Successfully processed secret {secret_name} in region {region}")
        yield serialize_datetime(secret_metadata)

    def _read_all_secrets_sequentially(self) -> Iterable[Mapping[str, Any]]:
        """
        Fallback method for sequential processing when no stream slices are provided.
        This maintains backwards compatibility and processes all regions sequentially.
        """
        for region in self._get_all_aws_regions():
            try:
                client = self._get_secretsmanager_client_for_region(region)
                paginator = client.get_paginator("list_secrets")
                for page in paginator.paginate():
                    for secret in page.get("SecretList", []):
                        secret_arn = secret.get("ARN")
                        secret_name = secret.get("Name")
                        
                        try:
                            # Get detailed metadata for this secret
                            response = client.describe_secret(SecretId=secret_arn)
                            
                            # Remove sensitive data - we only want metadata
                            secret_metadata = response.copy()
                            # Remove any potential secret value fields (defensive programming)
                            secret_metadata.pop("SecretString", None)
                            secret_metadata.pop("SecretBinary", None)
                            
                            # Add region information to the metadata
                            secret_metadata["Region"] = region
                            
                            yield serialize_datetime(secret_metadata)
                            
                        except Exception as e:
                            logging.warning(f"Cannot describe secret {secret_name} ({secret_arn}) in region {region}: {str(e)}")
                            continue
                            
            except Exception as e:
                logging.debug(f"Cannot access region {region}: {str(e)}")
                continue


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


# Base class for AWS KMS streams
class BaseKMSStream(Stream):
    """Base class for AWS KMS streams."""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._region_clients = {}

    def _get_kms_client_for_region(self, region: str):
        """Get or create a KMS client for a specific region."""
        if region not in self._region_clients:
            logging.info(f"Creating KMS client for region {region}")
            role_arn = self.config.get("role_arn")
            external_id = self.config.get("external_id")
            
            if role_arn:
                logging.info(f"Using assume role {role_arn} for region {region}")
                self._region_clients[region] = self._get_client_with_assume_role(
                    aws_service="kms", 
                    role_arn=role_arn, 
                    external_id=external_id, 
                    region=region
                )
            else:
                logging.info(f"Using default credentials for region {region}")
                self._region_clients[region] = boto3.client("kms", region_name=region)
            
            logging.info(f"Successfully created KMS client for region {region}")
        
        return self._region_clients[region]

    def _get_client_with_assume_role(self, aws_service: str, role_arn: str, external_id: str = None, region: str = None):
        """Create a client using assume role credentials for a specific region."""
        
        try:
            sts_client = boto3.client("sts")
            assume_role_kwargs = {
                "RoleArn": role_arn,
                "RoleSessionName": f"airbyte-kms-{region}"
            }
            if external_id:
                assume_role_kwargs["ExternalId"] = external_id
                
            credentials = sts_client.assume_role(**assume_role_kwargs)["Credentials"]
            
            # Create a new session with the assumed role credentials
            session = boto3.Session(
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
                region_name=region
            )
            
            return session.client(aws_service)
            
        except Exception as e:
            logging.error(f"Failed to assume role {role_arn} for region {region}: {str(e)}")
            raise

    def _get_all_aws_regions(self):
        """Get list of AWS regions that support KMS."""
        # Only include commonly available regions that support KMS
        # Excluding opt-in regions that may cause authentication issues
        return [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1', 'eu-north-1',
            'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2', 'ap-south-1',
            'ca-central-1', 'sa-east-1'
        ]


class KMSKeysStream(BaseKMSStream):
    """Stream to read AWS KMS keys metadata across all regions."""
    name = "kms_key"
    primary_key = "KeyId"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "KeyId": {"type": "string"},
                "Arn": {"type": "string"},
                "AWSAccountId": {"type": ["string", "null"]},
                "CreationDate": {"type": ["string", "null"], "format": "date-time"},
                "CustomerMasterKeySpec": {"type": ["string", "null"]},
                "KeySpec": {"type": ["string", "null"]},
                "KeyUsage": {"type": ["string", "null"]},
                "KeyState": {"type": ["string", "null"]},
                "DeletionDate": {"type": ["string", "null"], "format": "date-time"},
                "ValidTo": {"type": ["string", "null"], "format": "date-time"},
                "Origin": {"type": ["string", "null"]},
                "ExpirationModel": {"type": ["string", "null"]},
                "KeyManager": {"type": ["string", "null"]},
                "Description": {"type": ["string", "null"]},
                "Enabled": {"type": ["boolean", "null"]},
                "EncryptionAlgorithms": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "SigningAlgorithms": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "MultiRegion": {"type": ["boolean", "null"]},
                "MultiRegionConfiguration": {
                    "type": ["object", "null"],
                    "properties": {
                        "MultiRegionKeyType": {"type": ["string", "null"]},
                        "PrimaryKey": {
                            "type": ["object", "null"],
                            "properties": {
                                "Arn": {"type": ["string", "null"]},
                                "Region": {"type": ["string", "null"]}
                            }
                        },
                        "ReplicaKeys": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "Arn": {"type": ["string", "null"]},
                                    "Region": {"type": ["string", "null"]}
                                }
                            }
                        }
                    }
                },
                "PendingDeletionWindowInDays": {"type": ["integer", "null"]},
                "MacAlgorithms": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "XksKeyConfiguration": {
                    "type": ["object", "null"],
                    "properties": {
                        "Id": {"type": ["string", "null"]}
                    }
                },
                "Tags": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "TagKey": {"type": "string"},
                            "TagValue": {"type": "string"}
                        }
                    }
                },
                "Aliases": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "AliasName": {"type": ["string", "null"]},
                            "AliasArn": {"type": ["string", "null"]},
                            "TargetKeyId": {"type": ["string", "null"]},
                            "CreationDate": {"type": ["string", "null"], "format": "date-time"},
                            "LastUpdatedDate": {"type": ["string", "null"], "format": "date-time"}
                        }
                    }
                },
                "Region": {"type": "string"}
            }
        }

    def stream_slices(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Create slices for each region and key combination to enable concurrent processing.
        Each slice contains a region and key ID to process.
        """
        slice_count = 0
        regions_processed = 0
        
        for region in self._get_all_aws_regions():
            logging.info(f"Checking region {region} for KMS keys...")
            client = self._get_kms_client_for_region(region)
            paginator = client.get_paginator("list_keys")
            
            keys_in_region = 0
            for page in paginator.paginate():
                for key in page.get("Keys", []):
                    keys_in_region += 1
                    slice_count += 1
                    yield {
                        "region": region,
                        "key_id": key.get("KeyId")
                    }
            
            if keys_in_region > 0:
                logging.info(f"Found {keys_in_region} KMS keys in region {region}")
            else:
                logging.info(f"No KMS keys found in region {region}")
            regions_processed += 1
        
        logging.info(f"Processed {regions_processed} regions, generated {slice_count} slices")

    def read_records(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Process metadata for a single KMS key (from the stream slice).
        This allows concurrent processing of different keys across regions.
        """
        if not stream_slice:
            # Fallback for backwards compatibility - shouldn't happen in concurrent mode
            logging.warning("No stream slice provided, falling back to sequential processing")
            yield from self._read_all_keys_sequentially()
            return

        region = stream_slice["region"]
        key_id = stream_slice["key_id"]

        logging.info(f"Processing KMS key {key_id} in region {region}")

        client = self._get_kms_client_for_region(region)
        
        # Get detailed metadata for this specific key
        response = client.describe_key(KeyId=key_id)
        key_metadata = response.get("KeyMetadata", {})
        
        # Add region information to the metadata
        key_metadata["Region"] = region
        
        # Get tags for the key
        try:
            tags_response = client.list_resource_tags(KeyId=key_id)
            key_metadata["Tags"] = tags_response.get("Tags", [])
        except Exception as e:
            logging.warning(f"Cannot get tags for key {key_id} in region {region}: {str(e)}")
            key_metadata["Tags"] = []
        
        # Get aliases for the key
        try:
            aliases_paginator = client.get_paginator("list_aliases")
            aliases = []
            for alias_page in aliases_paginator.paginate():
                for alias in alias_page.get("Aliases", []):
                    if alias.get("TargetKeyId") == key_id:
                        aliases.append(alias)
            key_metadata["Aliases"] = aliases
        except Exception as e:
            logging.warning(f"Cannot get aliases for key {key_id} in region {region}: {str(e)}")
            key_metadata["Aliases"] = []
        
        logging.info(f"Successfully processed KMS key {key_id} in region {region}")
        yield serialize_datetime(key_metadata)

    def _read_all_keys_sequentially(self) -> Iterable[Mapping[str, Any]]:
        """
        Fallback method for sequential processing when no stream slices are provided.
        This maintains backwards compatibility and processes all regions sequentially.
        """
        for region in self._get_all_aws_regions():
            try:
                client = self._get_kms_client_for_region(region)
                paginator = client.get_paginator("list_keys")
                for page in paginator.paginate():
                    for key in page.get("Keys", []):
                        key_id = key.get("KeyId")
                        
                        try:
                            # Get detailed metadata for this key
                            response = client.describe_key(KeyId=key_id)
                            key_metadata = response.get("KeyMetadata", {})
                            
                            # Add region information to the metadata
                            key_metadata["Region"] = region
                            
                            # Get tags for the key
                            try:
                                tags_response = client.list_resource_tags(KeyId=key_id)
                                key_metadata["Tags"] = tags_response.get("Tags", [])
                            except Exception as e:
                                logging.warning(f"Cannot get tags for key {key_id} in region {region}: {str(e)}")
                                key_metadata["Tags"] = []
                            
                            # Get aliases for the key
                            try:
                                aliases_paginator = client.get_paginator("list_aliases")
                                aliases = []
                                for alias_page in aliases_paginator.paginate():
                                    for alias in alias_page.get("Aliases", []):
                                        if alias.get("TargetKeyId") == key_id:
                                            aliases.append(alias)
                                key_metadata["Aliases"] = aliases
                            except Exception as e:
                                logging.warning(f"Cannot get aliases for key {key_id} in region {region}: {str(e)}")
                                key_metadata["Aliases"] = []
                            
                            yield serialize_datetime(key_metadata)
                            
                        except Exception as e:
                            logging.warning(f"Cannot describe key {key_id} in region {region}: {str(e)}")
                            continue
                            
            except Exception as e:
                logging.debug(f"Cannot access region {region}: {str(e)}")
                continue


# Base class for AWS EKS streams
class BaseEKSStream(Stream):
    """Base class for AWS EKS streams."""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._region_clients = {}

    def _get_eks_client_for_region(self, region: str):
        """Get or create an EKS client for a specific region."""
        if region not in self._region_clients:
            logging.info(f"Creating EKS client for region {region}")
            role_arn = self.config.get("role_arn")
            external_id = self.config.get("external_id")
            
            if role_arn:
                logging.info(f"Using assume role {role_arn} for region {region}")
                self._region_clients[region] = self._get_client_with_assume_role(
                    aws_service="eks", 
                    role_arn=role_arn, 
                    external_id=external_id, 
                    region=region
                )
            else:
                logging.info(f"Using default credentials for region {region}")
                self._region_clients[region] = boto3.client("eks", region_name=region)
            
            logging.info(f"Successfully created EKS client for region {region}")
        
        return self._region_clients[region]

    def _get_client_with_assume_role(self, aws_service: str, role_arn: str, external_id: str = None, region: str = None):
        """Create a client using assume role credentials for a specific region."""
        
        try:
            sts_client = boto3.client("sts")
            assume_role_kwargs = {
                "RoleArn": role_arn,
                "RoleSessionName": f"airbyte-eks-{region}"
            }
            if external_id:
                assume_role_kwargs["ExternalId"] = external_id
                
            credentials = sts_client.assume_role(**assume_role_kwargs)["Credentials"]
            
            # Create a new session with the assumed role credentials
            session = boto3.Session(
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
                region_name=region
            )
            
            return session.client(aws_service)
            
        except Exception as e:
            logging.error(f"Failed to assume role {role_arn} for region {region}: {str(e)}")
            raise

    def _get_all_aws_regions(self):
        """Get list of AWS regions that support EKS."""
        # Only include commonly available regions that support EKS
        # Excluding opt-in regions that may cause authentication issues
        return [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1', 'eu-north-1',
            'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2', 'ap-south-1',
            'ca-central-1', 'sa-east-1'
        ]


class EKSClustersStream(BaseEKSStream):
    """Stream to read AWS EKS clusters metadata across all regions."""
    name = "eks_cluster"
    primary_key = "arn"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "arn": {"type": "string"},
                "createdAt": {"type": ["string", "null"], "format": "date-time"},
                "version": {"type": ["string", "null"]},
                "endpoint": {"type": ["string", "null"]},
                "roleArn": {"type": ["string", "null"]},
                "resourcesVpcConfig": {
                    "type": ["object", "null"],
                    "properties": {
                        "subnetIds": {
                            "type": ["array", "null"],
                            "items": {"type": "string"}
                        },
                        "securityGroupIds": {
                            "type": ["array", "null"],
                            "items": {"type": "string"}
                        },
                        "clusterSecurityGroupId": {"type": ["string", "null"]},
                        "vpcId": {"type": ["string", "null"]},
                        "endpointConfigResponse": {
                            "type": ["object", "null"],
                            "properties": {
                                "privateAccess": {"type": ["boolean", "null"]},
                                "publicAccess": {"type": ["boolean", "null"]},
                                "publicAccessCidrs": {
                                    "type": ["array", "null"],
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "kubernetesNetworkConfig": {
                    "type": ["object", "null"],
                    "properties": {
                        "serviceIpv4Cidr": {"type": ["string", "null"]},
                        "serviceIpv6Cidr": {"type": ["string", "null"]},
                        "ipFamily": {"type": ["string", "null"]}
                    }
                },
                "logging": {
                    "type": ["object", "null"],
                    "properties": {
                        "clusterLogging": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "types": {
                                        "type": ["array", "null"],
                                        "items": {"type": "string"}
                                    },
                                    "enabled": {"type": ["boolean", "null"]}
                                }
                            }
                        }
                    }
                },
                "identity": {
                    "type": ["object", "null"],
                    "properties": {
                        "oidc": {
                            "type": ["object", "null"],
                            "properties": {
                                "issuer": {"type": ["string", "null"]}
                            }
                        }
                    }
                },
                "status": {"type": ["string", "null"]},
                "certificateAuthority": {
                    "type": ["object", "null"],
                    "properties": {
                        "data": {"type": ["string", "null"]}
                    }
                },
                "clientRequestToken": {"type": ["string", "null"]},
                "platformVersion": {"type": ["string", "null"]},
                "tags": {
                    "type": ["object", "null"],
                    "additionalProperties": {"type": "string"}
                },
                "encryptionConfig": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "resources": {
                                "type": ["array", "null"],
                                "items": {"type": "string"}
                            },
                            "provider": {
                                "type": ["object", "null"],
                                "properties": {
                                    "keyArn": {"type": ["string", "null"]}
                                }
                            }
                        }
                    }
                },
                "connectorConfig": {
                    "type": ["object", "null"],
                    "properties": {
                        "activationId": {"type": ["string", "null"]},
                        "activationCode": {"type": ["string", "null"]},
                        "activationExpiry": {"type": ["string", "null"], "format": "date-time"},
                        "provider": {"type": ["string", "null"]},
                        "roleArn": {"type": ["string", "null"]}
                    }
                },
                "id": {"type": ["string", "null"]},
                "health": {
                    "type": ["object", "null"],
                    "properties": {
                        "issues": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": ["string", "null"]},
                                    "message": {"type": ["string", "null"]},
                                    "resourceIds": {
                                        "type": ["array", "null"],
                                        "items": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                },
                "outpostConfig": {
                    "type": ["object", "null"],
                    "properties": {
                        "outpostArns": {
                            "type": ["array", "null"],
                            "items": {"type": "string"}
                        },
                        "controlPlaneInstanceType": {"type": ["string", "null"]},
                        "controlPlanePlacement": {
                            "type": ["object", "null"],
                            "properties": {
                                "groupName": {"type": ["string", "null"]}
                            }
                        }
                    }
                },
                "accessConfig": {
                    "type": ["object", "null"],
                    "properties": {
                        "bootstrapClusterCreatorAdminPermissions": {"type": ["boolean", "null"]},
                        "authenticationMode": {"type": ["string", "null"]}
                    }
                },
                "region": {"type": "string"}
            }
        }

    def stream_slices(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Create slices for each region and cluster combination to enable concurrent processing.
        Each slice contains a region and cluster name to process.
        """
        slice_count = 0
        regions_processed = 0
        
        for region in self._get_all_aws_regions():
            logging.info(f"Checking region {region} for EKS clusters...")
            client = self._get_eks_client_for_region(region)
            paginator = client.get_paginator("list_clusters")
            
            clusters_in_region = 0
            for page in paginator.paginate():
                for cluster_name in page.get("clusters", []):
                    clusters_in_region += 1
                    slice_count += 1
                    yield {
                        "region": region,
                        "cluster_name": cluster_name
                    }
            
            if clusters_in_region > 0:
                logging.info(f"Found {clusters_in_region} EKS clusters in region {region}")
            else:
                logging.info(f"No EKS clusters found in region {region}")
            regions_processed += 1
        
        logging.info(f"Processed {regions_processed} regions, generated {slice_count} slices")

    def read_records(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Process metadata for a single EKS cluster (from the stream slice).
        This allows concurrent processing of different clusters across regions.
        """
        if not stream_slice:
            # Fallback for backwards compatibility - shouldn't happen in concurrent mode
            logging.warning("No stream slice provided, falling back to sequential processing")
            yield from self._read_all_clusters_sequentially()
            return

        region = stream_slice["region"]
        cluster_name = stream_slice["cluster_name"]

        logging.info(f"Processing EKS cluster {cluster_name} in region {region}")

        client = self._get_eks_client_for_region(region)
        
        # Get detailed metadata for this specific cluster
        response = client.describe_cluster(name=cluster_name)
        cluster_metadata = response.get("cluster", {})
        
        # Add region information to the metadata
        cluster_metadata["region"] = region
        
        logging.info(f"Successfully processed EKS cluster {cluster_name} in region {region}")
        yield serialize_datetime(cluster_metadata)

    def _read_all_clusters_sequentially(self) -> Iterable[Mapping[str, Any]]:
        """
        Fallback method for sequential processing when no stream slices are provided.
        This maintains backwards compatibility and processes all regions sequentially.
        """
        for region in self._get_all_aws_regions():
            try:
                client = self._get_eks_client_for_region(region)
                paginator = client.get_paginator("list_clusters")
                for page in paginator.paginate():
                    for cluster_name in page.get("clusters", []):
                        try:
                            # Get detailed metadata for this cluster
                            response = client.describe_cluster(name=cluster_name)
                            cluster_metadata = response.get("cluster", {})
                            
                            # Add region information to the metadata
                            cluster_metadata["region"] = region
                            
                            yield serialize_datetime(cluster_metadata)
                            
                        except Exception as e:
                            logging.warning(f"Cannot describe cluster {cluster_name} in region {region}: {str(e)}")
                            continue
                            
            except Exception as e:
                logging.debug(f"Cannot access region {region}: {str(e)}")
                continue


class IAMCredentialReportStream(BaseIAMStream):
    """Stream to read AWS IAM credential report data."""
    name = "iam_credential_report"
    primary_key = "arn"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user": {"type": "string"},
                "arn": {"type": "string"},
                "user_creation_time": {"type": ["string", "null"], "format": "date-time"},
                "password_enabled": {"type": ["string", "null"]},
                "password_last_used": {"type": ["string", "null"]},
                "password_last_changed": {"type": ["string", "null"], "format": "date-time"},
                "password_next_rotation": {"type": ["string", "null"]},
                "mfa_active": {"type": ["string", "null"]},
                "access_key_1_active": {"type": ["string", "null"]},
                "access_key_1_last_rotated": {"type": ["string", "null"], "format": "date-time"},
                "access_key_1_last_used_date": {"type": ["string", "null"], "format": "date-time"},
                "access_key_1_last_used_region": {"type": ["string", "null"]},
                "access_key_1_last_used_service": {"type": ["string", "null"]},
                "access_key_2_active": {"type": ["string", "null"]},
                "access_key_2_last_rotated": {"type": ["string", "null"], "format": "date-time"},
                "access_key_2_last_used_date": {"type": ["string", "null"], "format": "date-time"},
                "access_key_2_last_used_region": {"type": ["string", "null"]},
                "access_key_2_last_used_service": {"type": ["string", "null"]},
                "cert_1_active": {"type": ["string", "null"]},
                "cert_1_last_rotated": {"type": ["string", "null"], "format": "date-time"},
                "cert_2_active": {"type": ["string", "null"]},
                "cert_2_last_rotated": {"type": ["string", "null"], "format": "date-time"},
                "report_generated_time": {"type": ["string", "null"], "format": "date-time"}
            }
        }

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        import csv
        import io

        # Generate the credential report
        logging.info("Generating IAM credential report...")
        generate_response = self.iam.generate_credential_report()
        state = generate_response.get("State")
        
        # Wait for report generation if needed
        if state == "STARTED":
            logging.info("Credential report generation started, waiting for completion...")
            import time
            max_attempts = 30
            attempt = 0
            while attempt < max_attempts:
                time.sleep(2)
                try:
                    get_response = self.iam.get_credential_report()
                    break
                except Exception as e:
                    if "ReportNotPresent" in str(e):
                        attempt += 1
                        continue
                    else:
                        raise
            else:
                raise Exception("Credential report generation timed out after 30 attempts")
        else:
            # Report already exists or completed immediately
            get_response = self.iam.get_credential_report()
        
        # Get the CSV content and parse it directly
        report_content_bytes = get_response["Content"]
        # Properly decode bytes to string
        if isinstance(report_content_bytes, bytes):
            report_content = report_content_bytes.decode('utf-8')
        else:
            report_content = str(report_content_bytes)
        report_generated_time = get_response.get("GeneratedTime")
        
        logging.info("Successfully retrieved IAM credential report")
        logging.debug(f"Report content preview: {report_content[:200]}...")
        
        # Parse CSV content
        csv_reader = csv.DictReader(io.StringIO(report_content))
        
        record_count = 0
        for row in csv_reader:
            # Convert the row to our schema format
            record = {}
            for key, value in row.items():
                # Clean up field names (replace spaces with underscores, lowercase)
                clean_key = key.lower().replace(' ', '_').replace('/', '_')
                
                # Handle special values
                if value in ['N/A', 'no_information', 'not_supported']:
                    record[clean_key] = None
                elif value in ['TRUE', 'true']:
                    record[clean_key] = "true"
                elif value in ['FALSE', 'false']:
                    record[clean_key] = "false"
                else:
                    record[clean_key] = value if value else None
            
            # Add report generation timestamp (convert datetime to string)
            if report_generated_time:
                record["report_generated_time"] = report_generated_time.isoformat() if isinstance(report_generated_time, datetime) else report_generated_time
            else:
                record["report_generated_time"] = None
            
            record_count += 1
            yield serialize_datetime(record)
        
        logging.info(f"Successfully processed {record_count} records from credential report")


# Base class for AWS S3 streams
class BaseS3Stream(Stream):
    """Base class for AWS S3 streams."""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def _get_s3_client(self):
        """Get or create an S3 client."""
        if not hasattr(self, '_s3_client'):
            logging.info("Creating S3 client")
            role_arn = self.config.get("role_arn")
            external_id = self.config.get("external_id")
            
            if role_arn:
                logging.info(f"Using assume role {role_arn}")
                self._s3_client = self._get_client_with_assume_role(
                    aws_service="s3", 
                    role_arn=role_arn, 
                    external_id=external_id
                )
            else:
                logging.info("Using default credentials")
                self._s3_client = boto3.client("s3")
            
            logging.info("Successfully created S3 client")
        
        return self._s3_client

    def _get_client_with_assume_role(self, aws_service: str, role_arn: str, external_id: str = None):
        """Create a client using assume role credentials."""
        
        try:
            sts_client = boto3.client("sts")
            assume_role_kwargs = {
                "RoleArn": role_arn,
                "RoleSessionName": f"airbyte-s3"
            }
            if external_id:
                assume_role_kwargs["ExternalId"] = external_id
                
            credentials = sts_client.assume_role(**assume_role_kwargs)["Credentials"]
            
            # Create a new session with the assumed role credentials
            session = boto3.Session(
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"]
            )
            
            return session.client(aws_service)
            
        except Exception as e:
            logging.error(f"Failed to assume role {role_arn}: {str(e)}")
            raise


class S3BucketsStream(BaseS3Stream):
    """Stream to read AWS S3 buckets metadata."""
    name = "s3_bucket"
    primary_key = "Name"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "Name": {"type": "string"},
                "Arn": {"type": "string"},
                "CreationDate": {"type": ["string", "null"], "format": "date-time"},
                "Region": {"type": ["string", "null"]},
                "LocationConstraint": {"type": ["string", "null"]},
                "Versioning": {
                    "type": ["object", "null"],
                    "properties": {
                        "Status": {"type": ["string", "null"]},
                        "MfaDelete": {"type": ["string", "null"]}
                    }
                },
                "Encryption": {
                    "type": ["object", "null"],
                    "properties": {
                        "Rules": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "ApplyServerSideEncryptionByDefault": {
                                        "type": ["object", "null"],
                                        "properties": {
                                            "SSEAlgorithm": {"type": ["string", "null"]},
                                            "KMSMasterKeyID": {"type": ["string", "null"]}
                                        }
                                    },
                                    "BucketKeyEnabled": {"type": ["boolean", "null"]}
                                }
                            }
                        }
                    }
                },
                "PublicAccessBlock": {
                    "type": ["object", "null"],
                    "properties": {
                        "BlockPublicAcls": {"type": ["boolean", "null"]},
                        "IgnorePublicAcls": {"type": ["boolean", "null"]},
                        "BlockPublicPolicy": {"type": ["boolean", "null"]},
                        "RestrictPublicBuckets": {"type": ["boolean", "null"]}
                    }
                },
                "Lifecycle": {
                    "type": ["object", "null"],
                    "properties": {
                        "Rules": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "ID": {"type": ["string", "null"]},
                                    "Status": {"type": ["string", "null"]},
                                    "Filter": {"type": ["object", "null"]},
                                    "Transitions": {"type": ["array", "null"]},
                                    "Expiration": {"type": ["object", "null"]}
                                }
                            }
                        }
                    }
                },
                "Tagging": {
                    "type": ["object", "null"],
                    "properties": {
                        "TagSet": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "Key": {"type": "string"},
                                    "Value": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "Logging": {
                    "type": ["object", "null"],
                    "properties": {
                        "TargetBucket": {"type": ["string", "null"]},
                        "TargetPrefix": {"type": ["string", "null"]}
                    }
                },
                "Website": {
                    "type": ["object", "null"],
                    "properties": {
                        "IndexDocument": {
                            "type": ["object", "null"],
                            "properties": {
                                "Suffix": {"type": ["string", "null"]}
                            }
                        },
                        "ErrorDocument": {
                            "type": ["object", "null"],
                            "properties": {
                                "Key": {"type": ["string", "null"]}
                            }
                        }
                    }
                },
                "CORS": {
                    "type": ["object", "null"],
                    "properties": {
                        "CORSRules": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "AllowedMethods": {"type": ["array", "null"]},
                                    "AllowedOrigins": {"type": ["array", "null"]},
                                    "AllowedHeaders": {"type": ["array", "null"]},
                                    "ExposeHeaders": {"type": ["array", "null"]},
                                    "MaxAgeSeconds": {"type": ["integer", "null"]}
                                }
                            }
                        }
                    }
                },
                "NotificationConfiguration": {
                    "type": ["object", "null"],
                    "properties": {
                        "TopicConfigurations": {"type": ["array", "null"]},
                        "QueueConfigurations": {"type": ["array", "null"]},
                        "LambdaConfigurations": {"type": ["array", "null"]}
                    }
                }
            }
        }

    def stream_slices(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Create slices for each bucket to enable concurrent processing.
        Each slice contains a bucket name to process.
        """
        slice_count = 0
        
        # S3 buckets are global resources - just list them once
        client = self._get_s3_client()
        
        logging.info("Listing S3 buckets...")
        response = client.list_buckets()
        
        for bucket in response.get("Buckets", []):
            bucket_name = bucket.get("Name")
            if bucket_name:
                slice_count += 1
                creation_date = bucket.get("CreationDate")
                # Convert datetime to string to avoid JSON serialization issues
                creation_date_str = creation_date.isoformat() if isinstance(creation_date, datetime) else creation_date
                yield {
                    "bucket_name": bucket_name,
                    "creation_date": creation_date_str
                }
        
        logging.info(f"Generated {slice_count} slices for S3 buckets")

    def read_records(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Process metadata for a single S3 bucket (from the stream slice).
        This allows concurrent processing of different buckets.
        """
        if not stream_slice:
            logging.warning("No stream slice provided for S3 bucket stream")
            return

        bucket_name = stream_slice["bucket_name"]
        creation_date = stream_slice["creation_date"]

        logging.info(f"Processing S3 bucket {bucket_name}")

        # Start with basic bucket information
        bucket_metadata = {
            "Name": bucket_name,
            "Arn": f"arn:aws:s3:::{bucket_name}",
            "CreationDate": creation_date,
            "Region": None,  # Skip region detection due to potential access issues
            "LocationConstraint": None
        }

        # Get S3 client for bucket operations
        client = self._get_s3_client()

        # Get versioning configuration
        try:
            versioning_response = client.get_bucket_versioning(Bucket=bucket_name)
            bucket_metadata["Versioning"] = {
                "Status": versioning_response.get("Status"),
                "MfaDelete": versioning_response.get("MfaDelete")
            }
        except client.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDenied']:
                # Access denied for this bucket configuration - skip it
                logging.info(f"Access denied for bucket versioning on {bucket_name}, skipping")
                bucket_metadata["Versioning"] = None
            else:
                # Re-raise unexpected errors
                raise

        # Get encryption configuration
        try:
            encryption_response = client.get_bucket_encryption(Bucket=bucket_name)
            bucket_metadata["Encryption"] = encryption_response.get("ServerSideEncryptionConfiguration")
        except client.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['NoSuchEncryptionConfiguration', 'ServerSideEncryptionConfigurationNotFoundError', 'AccessDenied']:
                # Expected when bucket has no encryption configured or access denied
                bucket_metadata["Encryption"] = None
            else:
                # Re-raise unexpected errors
                raise

        # Get public access block configuration
        try:
            pab_response = client.get_public_access_block(Bucket=bucket_name)
            bucket_metadata["PublicAccessBlock"] = pab_response.get("PublicAccessBlockConfiguration")
        except client.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['NoSuchPublicAccessBlockConfiguration', 'AccessDenied']:
                # Expected when bucket has no public access block configured or access denied
                bucket_metadata["PublicAccessBlock"] = None
            else:
                # Re-raise unexpected errors
                raise

        # Get lifecycle configuration
        try:
            lifecycle_response = client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            bucket_metadata["Lifecycle"] = {"Rules": lifecycle_response.get("Rules")}
        except client.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['NoSuchLifecycleConfiguration', 'AccessDenied']:
                # Expected when bucket has no lifecycle configured or access denied
                bucket_metadata["Lifecycle"] = None
            else:
                # Re-raise unexpected errors
                raise

        # Get tagging
        try:
            tagging_response = client.get_bucket_tagging(Bucket=bucket_name)
            bucket_metadata["Tagging"] = {"TagSet": tagging_response.get("TagSet")}
        except client.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['NoSuchTagSet', 'AccessDenied']:
                # Expected when bucket has no tags or access denied
                bucket_metadata["Tagging"] = None
            else:
                # Re-raise unexpected errors
                raise

        # Get logging configuration
        try:
            logging_response = client.get_bucket_logging(Bucket=bucket_name)
            logging_config = logging_response.get("LoggingEnabled")
            if logging_config:
                bucket_metadata["Logging"] = {
                    "TargetBucket": logging_config.get("TargetBucket"),
                    "TargetPrefix": logging_config.get("TargetPrefix")
                }
            else:
                bucket_metadata["Logging"] = None
        except client.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDenied']:
                # Access denied for logging configuration
                bucket_metadata["Logging"] = None
            else:
                # Re-raise unexpected errors
                raise

        # Get website configuration
        try:
            website_response = client.get_bucket_website(Bucket=bucket_name)
            bucket_metadata["Website"] = {
                "IndexDocument": website_response.get("IndexDocument"),
                "ErrorDocument": website_response.get("ErrorDocument")
            }
        except client.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['NoSuchWebsiteConfiguration', 'AccessDenied']:
                # Expected when bucket is not configured for website hosting or access denied
                bucket_metadata["Website"] = None
            else:
                # Re-raise unexpected errors
                raise

        # Get CORS configuration
        try:
            cors_response = client.get_bucket_cors(Bucket=bucket_name)
            bucket_metadata["CORS"] = {"CORSRules": cors_response.get("CORSRules")}
        except client.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['NoSuchCORSConfiguration', 'AccessDenied']:
                # Expected when bucket has no CORS configured or access denied
                bucket_metadata["CORS"] = None
            else:
                # Re-raise unexpected errors
                raise

        # Get notification configuration
        try:
            notification_response = client.get_bucket_notification_configuration(Bucket=bucket_name)
            bucket_metadata["NotificationConfiguration"] = {
                "TopicConfigurations": notification_response.get("TopicConfigurations"),
                "QueueConfigurations": notification_response.get("QueueConfigurations"),
                "LambdaConfigurations": notification_response.get("LambdaConfigurations")
            }
        except client.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDenied']:
                # Access denied for notification configuration
                bucket_metadata["NotificationConfiguration"] = None
            else:
                # Re-raise unexpected errors
                raise

        logging.info(f"Successfully processed S3 bucket {bucket_name}")
        yield serialize_datetime(bucket_metadata)


# Base class for AWS Lambda streams
class BaseLambdaStream(Stream):
    """Base class for AWS Lambda streams."""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._region_clients = {}

    def _get_lambda_client_for_region(self, region: str):
        """Get or create a Lambda client for a specific region."""
        if region not in self._region_clients:
            logging.info(f"Creating Lambda client for region {region}")
            role_arn = self.config.get("role_arn")
            external_id = self.config.get("external_id")
            
            if role_arn:
                logging.info(f"Using assume role {role_arn} for region {region}")
                self._region_clients[region] = self._get_client_with_assume_role(
                    aws_service="lambda", 
                    role_arn=role_arn, 
                    external_id=external_id, 
                    region=region
                )
            else:
                logging.info(f"Using default credentials for region {region}")
                self._region_clients[region] = boto3.client("lambda", region_name=region)
            
            logging.info(f"Successfully created Lambda client for region {region}")
        
        return self._region_clients[region]

    def _get_client_with_assume_role(self, aws_service: str, role_arn: str, external_id: str = None, region: str = None):
        """Create a client using assume role credentials for a specific region."""
        
        try:
            sts_client = boto3.client("sts")
            assume_role_kwargs = {
                "RoleArn": role_arn,
                "RoleSessionName": f"airbyte-lambda-{region}"
            }
            if external_id:
                assume_role_kwargs["ExternalId"] = external_id
                
            credentials = sts_client.assume_role(**assume_role_kwargs)["Credentials"]
            
            # Create a new session with the assumed role credentials
            session = boto3.Session(
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
                region_name=region
            )
            
            return session.client(aws_service)
            
        except Exception as e:
            logging.error(f"Failed to assume role {role_arn} for region {region}: {str(e)}")
            raise

    def _get_all_aws_regions(self):
        """Get list of AWS regions that support Lambda."""
        # Only include commonly available regions that support Lambda
        # Excluding opt-in regions that may cause authentication issues
        return [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1', 'eu-north-1',
            'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2', 'ap-south-1',
            'ca-central-1', 'sa-east-1'
        ]


class LambdaFunctionsStream(BaseLambdaStream):
    """Stream to read AWS Lambda functions metadata across all regions."""
    name = "lambda_function"
    primary_key = "FunctionArn"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "FunctionName": {"type": "string"},
                "FunctionArn": {"type": "string"},
                "Runtime": {"type": ["string", "null"]},
                "Role": {"type": ["string", "null"]},
                "Handler": {"type": ["string", "null"]},
                "CodeSize": {"type": ["integer", "null"]},
                "Description": {"type": ["string", "null"]},
                "Timeout": {"type": ["integer", "null"]},
                "MemorySize": {"type": ["integer", "null"]},
                "LastModified": {"type": ["string", "null"], "format": "date-time"},
                "CodeSha256": {"type": ["string", "null"]},
                "Version": {"type": ["string", "null"]},
                "VpcConfig": {
                    "type": ["object", "null"],
                    "properties": {
                        "SubnetIds": {
                            "type": ["array", "null"],
                            "items": {"type": "string"}
                        },
                        "SecurityGroupIds": {
                            "type": ["array", "null"],
                            "items": {"type": "string"}
                        },
                        "VpcId": {"type": ["string", "null"]}
                    }
                },
                "Environment": {
                    "type": ["object", "null"],
                    "properties": {
                        "Variables": {
                            "type": ["object", "null"],
                            "additionalProperties": {"type": "string"}
                        },
                        "Error": {
                            "type": ["object", "null"],
                            "properties": {
                                "ErrorCode": {"type": ["string", "null"]},
                                "Message": {"type": ["string", "null"]}
                            }
                        }
                    }
                },
                "DeadLetterConfig": {
                    "type": ["object", "null"],
                    "properties": {
                        "TargetArn": {"type": ["string", "null"]}
                    }
                },
                "KMSKeyArn": {"type": ["string", "null"]},
                "TracingConfig": {
                    "type": ["object", "null"],
                    "properties": {
                        "Mode": {"type": ["string", "null"]}
                    }
                },
                "MasterArn": {"type": ["string", "null"]},
                "RevisionId": {"type": ["string", "null"]},
                "Layers": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "Arn": {"type": ["string", "null"]},
                            "CodeSize": {"type": ["integer", "null"]},
                            "SigningProfileVersionArn": {"type": ["string", "null"]},
                            "SigningJobArn": {"type": ["string", "null"]}
                        }
                    }
                },
                "State": {"type": ["string", "null"]},
                "StateReason": {"type": ["string", "null"]},
                "StateReasonCode": {"type": ["string", "null"]},
                "LastUpdateStatus": {"type": ["string", "null"]},
                "LastUpdateStatusReason": {"type": ["string", "null"]},
                "LastUpdateStatusReasonCode": {"type": ["string", "null"]},
                "FileSystemConfigs": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "Arn": {"type": ["string", "null"]},
                            "LocalMountPath": {"type": ["string", "null"]}
                        }
                    }
                },
                "PackageType": {"type": ["string", "null"]},
                "ImageConfigResponse": {
                    "type": ["object", "null"],
                    "properties": {
                        "ImageConfig": {
                            "type": ["object", "null"],
                            "properties": {
                                "EntryPoint": {
                                    "type": ["array", "null"],
                                    "items": {"type": "string"}
                                },
                                "Command": {
                                    "type": ["array", "null"],
                                    "items": {"type": "string"}
                                },
                                "WorkingDirectory": {"type": ["string", "null"]}
                            }
                        },
                        "Error": {
                            "type": ["object", "null"],
                            "properties": {
                                "ErrorCode": {"type": ["string", "null"]},
                                "Message": {"type": ["string", "null"]}
                            }
                        }
                    }
                },
                "SigningProfileVersionArn": {"type": ["string", "null"]},
                "SigningJobArn": {"type": ["string", "null"]},
                "Architectures": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "EphemeralStorage": {
                    "type": ["object", "null"],
                    "properties": {
                        "Size": {"type": ["integer", "null"]}
                    }
                },
                "Tags": {
                    "type": ["object", "null"],
                    "additionalProperties": {"type": "string"}
                },
                "Region": {"type": "string"}
            }
        }

    def stream_slices(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Create slices for each region and function combination to enable concurrent processing.
        Each slice contains a region and function name to process.
        """
        slice_count = 0
        regions_processed = 0
        
        for region in self._get_all_aws_regions():
            logging.info(f"Checking region {region} for Lambda functions...")
            client = self._get_lambda_client_for_region(region)
            paginator = client.get_paginator("list_functions")
            
            functions_in_region = 0
            for page in paginator.paginate():
                for function in page.get("Functions", []):
                    function_name = function.get("FunctionName")
                    if function_name:
                        functions_in_region += 1
                        slice_count += 1
                        yield {
                            "region": region,
                            "function_name": function_name
                        }
            
            if functions_in_region > 0:
                logging.info(f"Found {functions_in_region} Lambda functions in region {region}")
            else:
                logging.info(f"No Lambda functions found in region {region}")
            regions_processed += 1
        
        logging.info(f"Processed {regions_processed} regions, generated {slice_count} slices")

    def read_records(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Process metadata for a single Lambda function (from the stream slice).
        This allows concurrent processing of different functions across regions.
        """
        if not stream_slice:
            # Fallback for backwards compatibility
            logging.warning("No stream slice provided, falling back to sequential processing")
            yield from self._read_all_functions_sequentially()
            return

        region = stream_slice["region"]
        function_name = stream_slice["function_name"]

        logging.info(f"Processing Lambda function {function_name} in region {region}")

        client = self._get_lambda_client_for_region(region)
        
        # Get detailed metadata for this specific function
        response = client.get_function(FunctionName=function_name)
        function_metadata = response.get("Configuration", {})
        
        # Add region information to the metadata
        function_metadata["Region"] = region
        
        # Get tags for the function
        try:
            tags_response = client.list_tags(Resource=function_metadata.get("FunctionArn", ""))
            function_metadata["Tags"] = tags_response.get("Tags", {})
        except Exception as e:
            logging.warning(f"Cannot get tags for function {function_name} in region {region}: {str(e)}")
            function_metadata["Tags"] = {}
        
        logging.info(f"Successfully processed Lambda function {function_name} in region {region}")
        yield serialize_datetime(function_metadata)

    def _read_all_functions_sequentially(self) -> Iterable[Mapping[str, Any]]:
        """
        Fallback method for sequential processing when no stream slices are provided.
        This maintains backwards compatibility and processes all regions sequentially.
        """
        for region in self._get_all_aws_regions():
            client = self._get_lambda_client_for_region(region)
            paginator = client.get_paginator("list_functions")
            for page in paginator.paginate():
                for function in page.get("Functions", []):
                    function_name = function.get("FunctionName")
                    if function_name:
                        response = client.get_function(FunctionName=function_name)
                        function_metadata = response.get("Configuration", {})
                        function_metadata["Region"] = region
                        
                        # Get tags
                        try:
                            tags_response = client.list_tags(Resource=function_metadata.get("FunctionArn", ""))
                            function_metadata["Tags"] = tags_response.get("Tags", {})
                        except Exception:
                            function_metadata["Tags"] = {}
                        
                        yield serialize_datetime(function_metadata)


# Base class for AWS EC2 streams
class BaseEC2Stream(Stream):
    """Base class for AWS EC2 streams."""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._region_clients = {}

    def _get_ec2_client_for_region(self, region: str):
        """Get or create an EC2 client for a specific region."""
        if region not in self._region_clients:
            logging.info(f"Creating EC2 client for region {region}")
            role_arn = self.config.get("role_arn")
            external_id = self.config.get("external_id")
            
            if role_arn:
                logging.info(f"Using assume role {role_arn} for region {region}")
                self._region_clients[region] = self._get_client_with_assume_role(
                    aws_service="ec2", 
                    role_arn=role_arn, 
                    external_id=external_id, 
                    region=region
                )
            else:
                logging.info(f"Using default credentials for region {region}")
                self._region_clients[region] = boto3.client("ec2", region_name=region)
            
            logging.info(f"Successfully created EC2 client for region {region}")
        
        return self._region_clients[region]

    def _get_client_with_assume_role(self, aws_service: str, role_arn: str, external_id: str = None, region: str = None):
        """Create a client using assume role credentials for a specific region."""
        
        try:
            sts_client = boto3.client("sts")
            assume_role_kwargs = {
                "RoleArn": role_arn,
                "RoleSessionName": f"airbyte-ec2-{region}"
            }
            if external_id:
                assume_role_kwargs["ExternalId"] = external_id
                
            credentials = sts_client.assume_role(**assume_role_kwargs)["Credentials"]
            
            # Create a new session with the assumed role credentials
            session = boto3.Session(
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
                region_name=region
            )
            
            return session.client(aws_service)
            
        except Exception as e:
            logging.error(f"Failed to assume role {role_arn} for region {region}: {str(e)}")
            raise

    def _get_all_aws_regions(self):
        """Get list of AWS regions that support EC2."""
        # Only include commonly available regions that support EC2
        # Excluding opt-in regions that may cause authentication issues
        return [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1', 'eu-north-1',
            'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2', 'ap-south-1',
            'ca-central-1', 'sa-east-1'
        ]

    def _get_account_id(self):
        """Get the AWS account ID using STS."""
        if not hasattr(self, '_account_id'):
            try:
                role_arn = self.config.get("role_arn")
                external_id = self.config.get("external_id")
                
                if role_arn:
                    # Use STS with assume role
                    sts_client = boto3.client("sts")
                    assume_role_kwargs = {
                        "RoleArn": role_arn,
                        "RoleSessionName": "airbyte-account-lookup"
                    }
                    if external_id:
                        assume_role_kwargs["ExternalId"] = external_id
                        
                    credentials = sts_client.assume_role(**assume_role_kwargs)["Credentials"]
                    
                    # Create a new session with the assumed role credentials
                    session = boto3.Session(
                        aws_access_key_id=credentials["AccessKeyId"],
                        aws_secret_access_key=credentials["SecretAccessKey"],
                        aws_session_token=credentials["SessionToken"]
                    )
                    sts_client = session.client("sts")
                else:
                    # Use default credentials
                    sts_client = boto3.client("sts")
                
                # Get caller identity to extract account ID
                response = sts_client.get_caller_identity()
                self._account_id = response["Account"]
                logging.info(f"Retrieved AWS account ID: {self._account_id}")
                
            except Exception as e:
                logging.error(f"Failed to get AWS account ID: {str(e)}")
                raise
                
        return self._account_id


class EC2InstancesStream(BaseEC2Stream):
    """Stream to read AWS EC2 instances metadata across all regions."""
    name = "ec2_instance"
    primary_key = "InstanceId"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "properties": {
                "InstanceId": {"type": "string"},
                "Arn": {"type": "string"},
                "ImageId": {"type": ["string", "null"]},
                "State": {
                    "type": ["object", "null"],
                    "properties": {
                        "Code": {"type": ["integer", "null"]},
                        "Name": {"type": ["string", "null"]}
                    }
                },
                "PrivateDnsName": {"type": ["string", "null"]},
                "PublicDnsName": {"type": ["string", "null"]},
                "StateTransitionReason": {"type": ["string", "null"]},
                "InstanceType": {"type": ["string", "null"]},
                "KernelId": {"type": ["string", "null"]},
                "RamdiskId": {"type": ["string", "null"]},
                "Platform": {"type": ["string", "null"]},
                "Monitoring": {
                    "type": ["object", "null"],
                    "properties": {
                        "State": {"type": ["string", "null"]}
                    }
                },
                "SubnetId": {"type": ["string", "null"]},
                "VpcId": {"type": ["string", "null"]},
                "PrivateIpAddress": {"type": ["string", "null"]},
                "PublicIpAddress": {"type": ["string", "null"]},
                "StateReason": {
                    "type": ["object", "null"],
                    "properties": {
                        "Code": {"type": ["string", "null"]},
                        "Message": {"type": ["string", "null"]}
                    }
                },
                "Architecture": {"type": ["string", "null"]},
                "RootDeviceType": {"type": ["string", "null"]},
                "RootDeviceName": {"type": ["string", "null"]},
                "BlockDeviceMappings": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "DeviceName": {"type": ["string", "null"]},
                            "Ebs": {
                                "type": ["object", "null"],
                                "properties": {
                                    "AttachTime": {"type": ["string", "null"], "format": "date-time"},
                                    "DeleteOnTermination": {"type": ["boolean", "null"]},
                                    "Status": {"type": ["string", "null"]},
                                    "VolumeId": {"type": ["string", "null"]}
                                }
                            }
                        }
                    }
                },
                "VirtualizationType": {"type": ["string", "null"]},
                "InstanceLifecycle": {"type": ["string", "null"]},
                "SpotInstanceRequestId": {"type": ["string", "null"]},
                "ClientToken": {"type": ["string", "null"]},
                "Tags": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "Key": {"type": ["string", "null"]},
                            "Value": {"type": ["string", "null"]}
                        }
                    }
                },
                "SecurityGroups": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "GroupName": {"type": ["string", "null"]},
                            "GroupId": {"type": ["string", "null"]}
                        }
                    }
                },
                "SourceDestCheck": {"type": ["boolean", "null"]},
                "Hypervisor": {"type": ["string", "null"]},
                "NetworkInterfaces": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "NetworkInterfaceId": {"type": ["string", "null"]},
                            "SubnetId": {"type": ["string", "null"]},
                            "VpcId": {"type": ["string", "null"]},
                            "Description": {"type": ["string", "null"]},
                            "OwnerId": {"type": ["string", "null"]},
                            "Status": {"type": ["string", "null"]},
                            "MacAddress": {"type": ["string", "null"]},
                            "PrivateIpAddress": {"type": ["string", "null"]},
                            "PrivateDnsName": {"type": ["string", "null"]},
                            "SourceDestCheck": {"type": ["boolean", "null"]}
                        }
                    }
                },
                "IamInstanceProfile": {
                    "type": ["object", "null"],
                    "properties": {
                        "Arn": {"type": ["string", "null"]},
                        "Id": {"type": ["string", "null"]}
                    }
                },
                "EbsOptimized": {"type": ["boolean", "null"]},
                "SriovNetSupport": {"type": ["string", "null"]},
                "EnaSupport": {"type": ["boolean", "null"]},
                "LaunchTime": {"type": ["string", "null"], "format": "date-time"},
                "ProductCodes": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "ProductCodeId": {"type": ["string", "null"]},
                            "ProductCodeType": {"type": ["string", "null"]}
                        }
                    }
                },
                "UsageOperation": {"type": ["string", "null"]},
                "UsageOperationUpdateTime": {"type": ["string", "null"], "format": "date-time"},
                "PlatformDetails": {"type": ["string", "null"]},
                "BootMode": {"type": ["string", "null"]},
                "MetadataOptions": {
                    "type": ["object", "null"],
                    "properties": {
                        "State": {"type": ["string", "null"]},
                        "HttpTokens": {"type": ["string", "null"]},
                        "HttpPutResponseHopLimit": {"type": ["integer", "null"]},
                        "HttpEndpoint": {"type": ["string", "null"]},
                        "HttpProtocolIpv6": {"type": ["string", "null"]},
                        "InstanceMetadataTags": {"type": ["string", "null"]}
                    }
                },
                "EnclaveOptions": {
                    "type": ["object", "null"],
                    "properties": {
                        "Enabled": {"type": ["boolean", "null"]}
                    }
                },
                "HibernationOptions": {
                    "type": ["object", "null"],
                    "properties": {
                        "Configured": {"type": ["boolean", "null"]}
                    }
                },
                "Licenses": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "LicenseConfigurationArn": {"type": ["string", "null"]}
                        }
                    }
                },
                "MaintenanceOptions": {
                    "type": ["object", "null"],
                    "properties": {
                        "AutoRecovery": {"type": ["string", "null"]}
                    }
                },
                "CurrentInstanceBootMode": {"type": ["string", "null"]},
                "Region": {"type": "string"}
            }
        }

    def stream_slices(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Create slices for each region and instance combination to enable concurrent processing.
        Each slice contains a region and instance ID to process.
        """
        slice_count = 0
        regions_processed = 0
        
        for region in self._get_all_aws_regions():
            logging.info(f"Checking region {region} for EC2 instances...")
            client = self._get_ec2_client_for_region(region)
            paginator = client.get_paginator("describe_instances")
            
            instances_in_region = 0
            for page in paginator.paginate():
                for reservation in page.get("Reservations", []):
                    for instance in reservation.get("Instances", []):
                        instance_id = instance.get("InstanceId")
                        if instance_id:
                            instances_in_region += 1
                            slice_count += 1
                            yield {
                                "region": region,
                                "instance_id": instance_id
                            }
            
            if instances_in_region > 0:
                logging.info(f"Found {instances_in_region} EC2 instances in region {region}")
            else:
                logging.info(f"No EC2 instances found in region {region}")
            regions_processed += 1
        
        logging.info(f"Processed {regions_processed} regions, generated {slice_count} slices")

    def read_records(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Process metadata for a single EC2 instance (from the stream slice).
        This allows concurrent processing of different instances across regions.
        """
        if not stream_slice:
            # Fallback for backwards compatibility
            logging.warning("No stream slice provided, falling back to sequential processing")
            yield from self._read_all_instances_sequentially()
            return

        region = stream_slice["region"]
        instance_id = stream_slice["instance_id"]

        logging.info(f"Processing EC2 instance {instance_id} in region {region}")

        client = self._get_ec2_client_for_region(region)
        
        # Get detailed metadata for this specific instance
        response = client.describe_instances(InstanceIds=[instance_id])
        
        for reservation in response.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                if instance.get("InstanceId") == instance_id:
                    # Add region information to the metadata
                    instance["Region"] = region
                    
                    # Add ARN for the instance
                    account_id = self._get_account_id()
                    instance["Arn"] = f"arn:aws:ec2:{region}:{account_id}:instance/{instance_id}"
                    
                    logging.info(f"Successfully processed EC2 instance {instance_id} in region {region}")
                    yield serialize_datetime(instance)
                    return
        
        logging.warning(f"Instance {instance_id} not found in region {region}")

    def _read_all_instances_sequentially(self) -> Iterable[Mapping[str, Any]]:
        """
        Fallback method for sequential processing when no stream slices are provided.
        This maintains backwards compatibility and processes all regions sequentially.
        """
        for region in self._get_all_aws_regions():
            client = self._get_ec2_client_for_region(region)
            paginator = client.get_paginator("describe_instances")
            for page in paginator.paginate():
                for reservation in page.get("Reservations", []):
                    for instance in reservation.get("Instances", []):
                        instance["Region"] = region
                        
                        # Add ARN for the instance
                        account_id = self._get_account_id()
                        instance_id = instance.get("InstanceId")
                        instance["Arn"] = f"arn:aws:ec2:{region}:{account_id}:instance/{instance_id}"
                        
                        yield serialize_datetime(instance)
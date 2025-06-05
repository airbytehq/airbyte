from typing import Iterable, Mapping, Any

from airbyte_cdk.sources.streams import Stream


class BaseIAMStream(Stream):
    def __init__(self, iam_client, **kwargs):
        super().__init__(**kwargs)
        self.iam = iam_client


class IAMPoliciesStream(BaseIAMStream):
    name = "amazon/aws/iam.policy"
    primary_key = "Arn"

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        paginator = self.iam.get_paginator("list_policies")
        for page in paginator.paginate(Scope="Local"):
            for policy in page.get("Policies", []):
                yield policy


class IAMRolesStream(BaseIAMStream):
    name = "amazon/aws/iam.role"
    primary_key = "Arn"

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        paginator = self.iam.get_paginator("list_roles")
        for page in paginator.paginate():
            for role in page.get("Roles", []):
                yield role


class IAMUsersStream(BaseIAMStream):
    name = "amazon/aws/iam.user"
    primary_key = "Arn"

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        paginator = self.iam.get_paginator("list_users")
        for page in paginator.paginate():
            for user in page.get("Users", []):
                yield user


class IAMGroupsStream(BaseIAMStream):
    name = "amazon/aws/iam.group"
    primary_key = "Arn"

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        paginator = self.iam.get_paginator("list_groups")
        for page in paginator.paginate():
            for group in page.get("Groups", []):
                yield group


class IAMSAMLProvidersStream(BaseIAMStream):
    name = "amazon/aws/iam.saml-provider"
    primary_key = "Arn"

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        response = self.iam.list_saml_providers()
        for provider in response.get("SAMLProviderList", []):
            yield provider


class IAMUserInlinePoliciesStream(BaseIAMStream):
    name = "amazon/aws/iam.user-inline-policy"
    primary_key = None

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
    name = "amazon/aws/iam.role-inline-policy"
    primary_key = None

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

import logging
from typing import Any, List, Mapping, Tuple

import boto3
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import (
    IAMGroupsStream,
    IAMPoliciesStream,
    IAMSAMLProvidersStream,
    IAMRolesStream,
    IAMRoleInlinePoliciesStream,
    IAMUserInlinePoliciesStream,
    IAMUsersStream,
)


class SourceAwsIam(AbstractSource):
    def _get_iam_client(self, config: Mapping[str, Any]):
        role_arn = config.get("role_arn")
        external_id = config.get("external_id")
        if role_arn:
            sts = boto3.client("sts")
            assume_args = {"RoleArn": role_arn, "RoleSessionName": "airbyte-source-aws-iam"}
            if external_id:
                assume_args["ExternalId"] = external_id
            creds = sts.assume_role(**assume_args)["Credentials"]
            session = boto3.Session(
                aws_access_key_id=creds["AccessKeyId"],
                aws_secret_access_key=creds["SecretAccessKey"],
                aws_session_token=creds["SessionToken"],
            )
            return session.client("iam")
        return boto3.client("iam")

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            client = self._get_iam_client(config)
            client.list_users(MaxItems=1)
            return True, None
        except Exception as e:
            return False, str(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        client = self._get_iam_client(config)
        return [
            IAMPoliciesStream(client),
            IAMRolesStream(client),
            IAMUserInlinePoliciesStream(client),
            IAMGroupsStream(client),
            IAMSAMLProvidersStream(client),
            IAMUsersStream(client),
            IAMRoleInlinePoliciesStream(client),
        ]

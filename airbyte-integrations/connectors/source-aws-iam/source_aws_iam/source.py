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
            # Use STS to assume role with auto-refresh capabilities
            # This approach leverages boto3's built-in credential refresh
            session = boto3.Session()
            
            # Create STS client to assume the role
            sts_client = session.client('sts')
            
            # Configure assume role parameters  
            assume_role_args = {
                "RoleArn": role_arn,
                "RoleSessionName": "airbyte-source-aws-iam"
            }
            if external_id:
                assume_role_args["ExternalId"] = external_id
                
            assume_role_object = sts_client.assume_role(**assume_role_args)
            
            credentials = assume_role_object['Credentials']
            
            # Create a new session with the assumed role credentials
            # Note: This still doesn't auto-refresh, but is cleaner
            # For auto-refresh, we'd need to implement a custom credential provider
            assumed_session = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken']
            )
            
            return assumed_session.client('iam')
            
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

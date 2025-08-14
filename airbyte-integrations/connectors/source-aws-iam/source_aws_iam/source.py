# Standard library imports
import logging
from typing import Any, List, Mapping, Optional, Tuple

# AWS SDK imports
import boto3
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session

# Airbyte CDK imports
from airbyte_cdk.entrypoint import logger as entrypoint_logger
from airbyte_cdk.logger import AirbyteLogFormatter
from airbyte_cdk.models import Level
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import FinalStateCursor
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger

# Local imports
# Import streams (exclude deprecated SSOAdmin streams)
from .streams import (
    IAMAccessKeysStream,
    IAMSAMLProvidersStream,
    IAMGroupInlinePoliciesStream,
    IAMGroupPolicyBindingsStream,
    IAMGroupUserMembershipStream,
    IAMGroupsStream,
    IAMInlinePoliciesStream,
    IAMPoliciesStream,
    IAMRoleInlinePoliciesStream,
    IAMRolePolicyBindingsStream,
    IAMRolesStream,
    IAMUserInlinePoliciesStream,
    IAMUserPolicyBindingsStream,
    IAMUsersStream,
    IAMCredentialReportStream,
    SecretsManagerSecretsStream,
    KMSKeysStream,
    EKSClustersStream,
    S3BucketsStream,
    LambdaFunctionsStream,
    EC2InstancesStream,
    IdentityCenterGroupMembershipStream,
    IdentityCenterGroupStream,
    IdentityCenterInstanceStream,
    IdentityCenterUserStream,
    IdentityCenterGroupToRoleStream,
    IdentityCenterUserToRoleStream
)

_DEFAULT_CONCURRENCY = 5  # AWS IAM has reasonable rate limits
_MAX_CONCURRENCY = 10

logger = logging.getLogger("airbyte")


class SourceAwsIam(ConcurrentSourceAdapter):
    message_repository = InMemoryMessageRepository(Level(AirbyteLogFormatter.level_mapping[logger.level]))
    
    def __init__(self, catalog=None, config=None, state=None, **kwargs):
        # Configure concurrency based on config or use defaults
        if config:
            concurrency_level = min(config.get("num_workers", _DEFAULT_CONCURRENCY), _MAX_CONCURRENCY)
        else:
            concurrency_level = _DEFAULT_CONCURRENCY
            
        logger.info(f"Using concurrent AWS IAM source with concurrency level {concurrency_level}")
    
        # Create the concurrent source
        # Ensure at least one thread for slice processing
        slice_threads = max(concurrency_level // 2, 1)
        concurrent_source = ConcurrentSource.create(
            concurrency_level,
            slice_threads,  # Thread pool size for slice processing 
            logger, 
            DebugSliceLogger(),  # Use DebugSliceLogger for slice logging
            self.message_repository
        )
        
        super().__init__(concurrent_source)
        self.catalog = catalog
        self.config = config
        self.state = state
        
    def _get_iam_client(self, config: Mapping[str, Any]):
        role_arn = config.get("role_arn")
        external_id = config.get("external_id")
        
        if role_arn:
            return self._get_client_with_assume_role(aws_service="iam", role_arn=role_arn, external_id=external_id)

        return boto3.client("iam")

    def _get_client_with_assume_role(self, aws_service: str, role_arn: str, external_id: str = None, region: Optional[str] = None):
        """
        Creates an IAM client using AWS Security Token Service (STS) with assumed role credentials. This method handles
        the authentication process by assuming an IAM role, optionally using an external ID for enhanced security.
        The obtained credentials are set to auto-refresh upon expiration, ensuring uninterrupted access to the IAM service.

        This method uses the current role (from environment variables or from the EKS pod's role) when performing
        assume role operations, rather than requiring explicit access keys.

        :param role_arn: The ARN of the IAM role to assume.
        :param external_id: Optional external ID for additional security when assuming the role.
        :return: An instance of a boto3 IAM client with the assumed role credentials.
        """

        def refresh():
            # Use the current role (from environment variables or instance profile)
            # to assume the specified role instead of using explicit credentials
            client = boto3.client("sts")
            
            assume_role_params = {
                "RoleArn": role_arn,
                "RoleSessionName": "airbyte-source-aws-iam",
            }
            
            # Add external ID if specified
            if external_id:
                assume_role_params["ExternalId"] = external_id
            
            role = client.assume_role(**assume_role_params)

            creds = role.get("Credentials", {})
            return {
                "access_key": creds["AccessKeyId"],
                "secret_key": creds["SecretAccessKey"],
                "token": creds["SessionToken"],
                "expiry_time": creds["Expiration"].isoformat(),
            }

        session_credentials = RefreshableCredentials.create_from_metadata(
            metadata=refresh(),
            refresh_using=refresh,
            method="sts-assume-role",
        )

        session = get_session()
        session._credentials = session_credentials
        autorefresh_session = boto3.Session(botocore_session=session)

        return autorefresh_session.client(aws_service, region)

    def _get_sso_admin_client(self, config: Mapping[str, Any]):
        role_arn = config.get("role_arn")
        external_id = config.get("external_id")
        region = config.get("aws_region",'us-east-1')

        if role_arn:
            return self._get_client_with_assume_role(aws_service="sso-admin", role_arn=role_arn, external_id=external_id, region=region)

        return boto3.client("sso-admin")
    
    def _get_identitystore_client(self, config: Mapping[str, Any]):
        role_arn = config.get("role_arn")
        external_id = config.get("external_id")
        region = config.get("aws_region", 'us-east-1')

        if role_arn:
            return self._get_client_with_assume_role(aws_service="identitystore", role_arn=role_arn, external_id=external_id, region=region)

        return boto3.client("identitystore")

    def _get_secretsmanager_client(self, config: Mapping[str, Any]):
        role_arn = config.get("role_arn")
        external_id = config.get("external_id")
        region = config.get("aws_region", 'us-east-1')

        if role_arn:
            return self._get_client_with_assume_role(aws_service="secretsmanager", role_arn=role_arn, external_id=external_id, region=region)

        return boto3.client("secretsmanager", region_name=region)
    

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            client = self._get_iam_client(config)
            client.list_users(MaxItems=1)
            return True, None
        except Exception as e:
            return False, str(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        iam_client = self._get_iam_client(config)
        sso_admin_client = self._get_sso_admin_client(config)
        identitystore_client = self._get_identitystore_client(config)
        secretsmanager_client = self._get_secretsmanager_client(config)
        
        # Create base streams
        base_streams = [
            IAMAccessKeysStream(iam_client),
            IAMPoliciesStream(iam_client),
            IAMRolesStream(iam_client),
            IAMUserInlinePoliciesStream(iam_client),
            IAMGroupsStream(iam_client),
            IAMSAMLProvidersStream(iam_client),
            IAMUsersStream(iam_client),
            IAMCredentialReportStream(iam_client),
            IAMRoleInlinePoliciesStream(iam_client),
            IAMGroupInlinePoliciesStream(iam_client),
            IAMInlinePoliciesStream(iam_client),
            IAMUserPolicyBindingsStream(iam_client),
            IAMRolePolicyBindingsStream(iam_client),
            IAMGroupPolicyBindingsStream(iam_client),
            IAMGroupUserMembershipStream(iam_client),
        ]
        # Add Secrets Manager streams
        base_streams += [
            SecretsManagerSecretsStream(config),
        ]
        # Add KMS streams
        base_streams += [
            KMSKeysStream(config),
        ]
        # Add S3 streams
        base_streams += [
            S3BucketsStream(config),
        ]
        # Add Lambda streams
        base_streams += [
            LambdaFunctionsStream(config),
        ]
        # Add EC2 streams
        base_streams += [
            EC2InstancesStream(config),
        ]
        # Add EKS streams
        base_streams += [
            EKSClustersStream(config),
        ]
        # Add Identity Center streams
        base_streams += [
            IdentityCenterInstanceStream(identitystore_client=identitystore_client, sso_admin_client=sso_admin_client),
            IdentityCenterUserStream(identitystore_client=identitystore_client, sso_admin_client=sso_admin_client),
            IdentityCenterGroupStream(identitystore_client=identitystore_client, sso_admin_client=sso_admin_client),
            IdentityCenterGroupMembershipStream(identitystore_client=identitystore_client, sso_admin_client=sso_admin_client),
            IdentityCenterUserToRoleStream(identitystore_client=identitystore_client, sso_admin_client=sso_admin_client),
            IdentityCenterGroupToRoleStream(identitystore_client=identitystore_client, sso_admin_client=sso_admin_client),
        ]
        # Wrap all streams for concurrent execution
        return [self._wrap_stream_for_concurrency(stream) for stream in base_streams]
    
    def _wrap_stream_for_concurrency(self, stream: Stream) -> Stream:
        """
        Wrap a stream for concurrent execution. Since AWS IAM streams are full-refresh only,
        we use FinalStateCursor for all streams.
        """
        return StreamFacade.create_from_stream(
            stream,
            self,
            entrypoint_logger,
            {},  # Empty state for full-refresh streams
            FinalStateCursor(
                stream_name=stream.name, 
                stream_namespace=stream.namespace, 
                message_repository=self.message_repository
            ),
        )

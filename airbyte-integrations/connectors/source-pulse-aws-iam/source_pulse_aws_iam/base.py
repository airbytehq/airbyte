import boto3
from typing import Any, Dict, Mapping, Optional
from botocore.client import BaseClient
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session


class BaseAwsClient:
    def __init__(self, config: Mapping[str, Any]):
        self.config = config
        self.provider_config = config.get('provider', {})
        self._iam_client = None
        self._cloudtrail_client = None
        self._organizations_client = None
        self._access_analyzer_client = None
        self._session = None

    def get_session(self):
        if self._session is None:
            auth_type = self.provider_config.get('auth_type')

            if auth_type == 'role':
                self._session = self._get_role_session()
            elif auth_type == 'credentials':
                self._session = self._get_credentials_session()
            else:
                raise ValueError("Invalid authentication type")

        return self._session

    def get_iam_client(self) -> BaseClient:
        if self._iam_client is None:
            self._iam_client = self.get_session().client('iam', **self._get_base_client_args())
        return self._iam_client

    def get_cloudtrail_client(self) -> BaseClient:
        if self._cloudtrail_client is None:
            self._cloudtrail_client = self.get_session().client('cloudtrail', **self._get_base_client_args())
        return self._cloudtrail_client

    def get_organizations_client(self) -> BaseClient:
        if self._organizations_client is None:
            self._organizations_client = self.get_session().client('organizations', **self._get_base_client_args())
        return self._organizations_client

    def get_access_analyzer_client(self) -> BaseClient:
        if self._access_analyzer_client is None:
            self._access_analyzer_client = self.get_session().client('accessanalyzer', **self._get_base_client_args())
        return self._access_analyzer_client

    def _get_credentials_session(self) -> boto3.Session:
        session_kwargs = {
            'aws_access_key_id': self.provider_config['aws_access_key_id'],
            'aws_secret_access_key': self.provider_config['aws_secret_access_key'],
            'region_name': self.provider_config.get('region', 'us-east-1')
        }
        return boto3.Session(**session_kwargs)

    def _get_role_session(self) -> boto3.Session:
        def refresh_credentials():
            sts_client = self._get_sts_client()
            assume_role_params = {
                'RoleArn': self.provider_config['role_arn'],
                'RoleSessionName': 'airbyte-iam-session'
            }

            if external_id := self.provider_config.get('external_id'):
                assume_role_params['ExternalId'] = external_id

            try:
                role = sts_client.assume_role(**assume_role_params)
                credentials = role.get('Credentials', {})

                return {
                    'access_key': credentials['AccessKeyId'],
                    'secret_key': credentials['SecretAccessKey'],
                    'token': credentials['SessionToken'],
                    'expiry_time': credentials['Expiration'].isoformat()
                }
            except Exception as e:
                raise Exception(f"Failed to assume role: {str(e)}")

        session_credentials = RefreshableCredentials.create_from_metadata(
            metadata=refresh_credentials(),
            refresh_using=refresh_credentials,
            method='sts-assume-role'
        )

        session = get_session()
        session._credentials = session_credentials
        return boto3.Session(botocore_session=session)

    def _get_sts_client(self) -> BaseClient:
        client_kwargs = self._get_base_client_args()

        if sts_creds := self.provider_config.get('sts_credentials'):
            client_kwargs.update({
                'aws_access_key_id': sts_creds['access_key_id'],
                'aws_secret_access_key': sts_creds['secret_access_key']
            })
            if session_token := sts_creds.get('session_token'):
                client_kwargs['aws_session_token'] = session_token

        if endpoint := self.provider_config.get('sts_endpoint'):
            client_kwargs['endpoint_url'] = endpoint

        return boto3.client('sts', **client_kwargs)

    def _get_base_client_args(self) -> Dict[str, Any]:
        args = {
            'region_name': self.provider_config.get('region', 'us-east-1')
        }

        if endpoint := self.provider_config.get('endpoint'):
            args['endpoint_url'] = endpoint

        if proxy := self.provider_config.get('proxy'):
            args['proxy'] = proxy

        if retry_config := self.provider_config.get('retry_config'):
            args['config'] = retry_config

        return args

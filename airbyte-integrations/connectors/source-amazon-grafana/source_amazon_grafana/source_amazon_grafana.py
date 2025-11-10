# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import datetime
import hashlib
import hmac
import json
import logging
from typing import Iterable, List, Mapping, Any, Optional

import boto3
from botocore.exceptions import ClientError
import requests

from airbyte_cdk.logger import init_logger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConnectorSpecification,
    Status,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import Source

logger = logging.getLogger("airbyte")

class SigV4Authenticator:
    def __init__(self, access_key: str, secret_key: str, region: str, service: str = "grafana"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.service = service
        logger.debug(f"SigV4 Initialized for service: {self.service}, region: {self.region}")

    def sign(self, key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def get_signature_key(self, date_stamp: str) -> bytes:
        k_date = self.sign(("AWS4" + self.secret_key).encode("utf-8"), date_stamp)
        k_region = self.sign(k_date, self.region)
        k_service = self.sign(k_region, self.service)
        k_signing = self.sign(k_service, "aws4_request")
        return k_signing

    def add_auth(self, method: str, url: str, headers: Mapping[str, str], body: bytes = b""):
        t = datetime.datetime.utcnow()
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")
        parsed_url = urlparse(url)
        
        canonical_uri = parsed_url.path or "/"
        canonical_querystring = parsed_url.query
        
        netloc = parsed_url.netloc
        if ":" in netloc:
             netloc = netloc.split(":")[0]

        payload_hash = hashlib.sha256(body or b"").hexdigest()
        
        if body and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        canonical_headers = f"host:{netloc}\n" + f"x-amz-date:{amz_date}\n"
        signed_headers = "host;x-amz-date"
        
        if "Content-Type" in headers:
            canonical_headers += f"content-type:{headers['Content-Type'].strip().lower()}\n"
            signed_headers += ";content-type"

        canonical_request = (
            method
            + "\n"
            + canonical_uri
            + "\n"
            + canonical_querystring
            + "\n"
            + canonical_headers
            + "\n"
            + signed_headers
            + "\n"
            + payload_hash
        )

        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.region}/{self.service}/aws4_request"
        string_to_sign = (
            algorithm + "\n" + amz_date + "\n" + credential_scope + "\n" + hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        )

        signing_key = self.get_signature_key(date_stamp)
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        authorization_header = (
            f"{algorithm} Credential={self.access_key}/{credential_scope}, " 
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        headers["x-amz-date"] = amz_date
        headers["Authorization"] = authorization_header
        headers["host"] = netloc
        
        logger.debug(f"SigV4 Auth generated for {method} {canonical_uri}")


class BaseGrafanaStream:
    token: Optional[str] = None
    token_id: Optional[str] = None

    def __init__(self, config: dict):
        self.config = config
        self.workspace_id = config["workspace_id"]
        self.region = config["region"]
        self.service_account_id = config["service_account_id"]

        self.grafana_client = boto3.client("grafana",
                                           region_name=self.region,
                                           aws_access_key_id=config["aws_access_key_id"],
                                           aws_secret_access_key=config["aws_secret_access_key"])

        if BaseGrafanaStream.token is None:
            self._ensure_token_created()

    def _ensure_token_created(self):
        if BaseGrafanaStream.token is None:
            try:
                token, token_id = self._create_token()
                BaseGrafanaStream.token = token
                BaseGrafanaStream.token_id = token_id
                logger.info(f"Created service account token with id {token_id}")
            except Exception as e:
                logger.error(f"Failed to create service account token: {e}")
                raise

    def _create_token(self) -> (str, str):
        existing_tokens = self.grafana_client.list_workspace_service_account_tokens(
            workspaceId=self.workspace_id,
            serviceAccountId=self.service_account_id
        )

        for t in existing_tokens.get("serviceAccountTokens", []):
            if t.get("name") == "airbyte-temp-token":
                logger.info(f"Deleting existing token {t.get('id')}")
                self.grafana_client.delete_workspace_service_account_token(
                    workspaceId=self.workspace_id,
                    serviceAccountId=self.service_account_id,
                    tokenId=t.get("id")
                )

        creates = self.grafana_client.create_workspace_service_account_token(
            workspaceId=self.workspace_id,
            serviceAccountId=self.service_account_id,
            name="airbyte-temp-token",
            secondsToLive=3600
        )

        token_key = creates["serviceAccountToken"]["key"]
        token_id = creates["serviceAccountToken"]["id"]
        return token_key, token_id

    def _delete_token(self, token_id: str):
        try:
            self.grafana_client.delete_workspace_service_account_token(
                workspaceId=self.workspace_id,
                serviceAccountId=self.service_account_id,
                tokenId=token_id
            )
            logger.info(f"Deleted service account token id {token_id}")
        except ClientError as e:
            logger.warning(f"Failed to delete token id {token_id}: {e}")

    def request(self, path: str, method: str = "GET", body: Optional[bytes] = None) -> Any:
        self._ensure_token_created()

        url = f"https://{self.workspace_id}.grafana-workspace.{self.region}.amazonaws.com{path}"

        headers = {
            "Authorization": f"Bearer {BaseGrafanaStream.token}",
            "Accept": "application/json"
        }
        if body is not None:
            headers["Content-Type"] = "application/json"

        resp = requests.request(method, url, headers=headers, data=body)
        if resp.status_code == 401:
            logger.error(f"Unauthorized accessing Grafana API at {path} - verify token validity.")
        resp.raise_for_status()
        return resp.json()

    def read_records(self) -> Iterable[Mapping[str, Any]]:
        raise NotImplementedError()


class UsersStream(BaseGrafanaStream):
    def read_records(self) -> Iterable[Mapping[str, Any]]:
        data = self.request("/api/org/users")
        for user in data:
            user["id"] = user.pop("userId")
            yield user


class TeamsStream(BaseGrafanaStream):
    def read_records(self) -> Iterable[Mapping[str, Any]]:
        data = self.request("/api/teams/search")
        for team in data.get("teams", []):
            yield team


class SourceAmazonGrafana(Source):
    def check(self, logger, config) -> AirbyteConnectionStatus:
        try:
            stream = UsersStream(config)
            next(stream.read_records())
            if stream.token_id:
                stream._delete_token(stream.token_id)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))

    def discover(self, logger, config) -> AirbyteCatalog:
        schemas = {
            "users": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "orgId": {"type": "integer"},
                    "name": {"type": "string"},
                    "login": {"type": "string"},
                    "role": {"type": "string"},
                    "email": {"type": "string"},
                    "avatarUrl": {"type": "string"},
                    "lastSeenAt": {"type": "string", "format": "date-time"},
                    "isDisabled": {"type": "boolean"},
                    "authLabels": {"type": "array", "items": {"type": "string"}},
                    "isExternallySynced": {"type": "boolean"},
                },
                "required": ["id", "name"],
                "additionalProperties": True,
            },
            "teams": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "uid": {"type": "string"},
                    "orgId": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "memberCount": {"type": "integer"},
                    "permission": {"type": "integer"},
                    "accessControl": {"type": ["null", "object"]},
                },
                "required": ["id", "name"],
                "additionalProperties": True,
            }
        }
    
        streams = [
            AirbyteStream(
                name="users",
                json_schema=schemas["users"],
                supported_sync_modes=[SyncMode.full_refresh],
                source_defined_primary_key=[["id"]],
            ),
            AirbyteStream(
                name="teams",
                json_schema=schemas["teams"],
                supported_sync_modes=[SyncMode.full_refresh],
                source_defined_primary_key=[["id"]],
            )
        ]
    
        return AirbyteCatalog(streams=streams)

    def streams(self, config: Mapping[str, Any]) -> List[BaseGrafanaStream]:
        return [UsersStream(config), TeamsStream(config)]

    def read(self, logger, config, configured_catalog, state=None):
        from datetime import datetime
        streams_to_read = self.streams(config)
        token_manager = streams_to_read[0] if streams_to_read else None
        try:
            for stream in streams_to_read:
                stream_name = stream.__class__.__name__.replace("Stream", "").lower()
                for record in stream.read_records():
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(
                            stream=stream_name,
                            data=record,
                            emitted_at=int(datetime.now().timestamp() * 1000),
                        ),
                    )
        finally:
            if token_manager and token_manager.token_id is not None:
                token_manager._delete_token(token_manager.token_id)

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/sources/amazon-grafana",
            connectionSpecification={
                "type": "object",
                "title": "Amazon Grafana Source Spec",
                "required": ["workspace_id", "region", "service_account_id", "aws_access_key_id", "aws_secret_access_key"],
                "properties": {
                    "workspace_id": {"type": "string", "description": "Grafana workspace ID", "order": 0},
                    "region": {
                        "type": "string",
                        "enum": [
                            "af-south-1", "ap-east-1", "ap-northeast-1", "ap-northeast-2", "ap-northeast-3",
                            "ap-south-1", "ap-south-2", "ap-southeast-1", "ap-southeast-2", "ap-southeast-3",
                            "ap-southeast-4", "ca-central-1", "ca-west-1", "cn-north-1", "cn-northwest-1",
                            "eu-central-1", "eu-central-2", "eu-north-1", "eu-south-1", "eu-south-2",
                            "eu-west-1", "eu-west-2", "eu-west-3", "il-central-1", "me-central-1", "me-south-1",
                            "sa-east-1", "us-east-1", "us-east-2", "us-gov-east-1", "us-gov-west-1", "us-west-1", "us-west-2",
                        ],
                        "default": "eu-central-1",
                        "description": "AWS region of the workspace",
                        "title": "AWS Region",
                        "order": 1,
                    },
                    "service_account_id": {"type": "string", "description": "ID Service Account used for token generation", "order": 2},
                    "aws_access_key_id": {"type": "string", "description": "AWS Access Key ID used for SigV4 authentication", "title": "AWS IAM Access Key ID", "airbyte_secret": True, "order": 3},
                    "aws_secret_access_key": {"type": "string", "description": "AWS Secret Access Key used for SigV4 authentication", "title": "AWS IAM Secret Key", "airbyte_secret": True, "order": 4},
                },
                "additionalProperties": True,
            },
        )
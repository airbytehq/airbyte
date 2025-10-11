# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import datetime
import hashlib
import hmac
from typing import Iterable

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


class SigV4Authenticator:
    def __init__(self, access_key, secret_key, region, service="aps"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.service = service

    def sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def get_signature_key(self, date_stamp):
        k_date = self.sign(("AWS4" + self.secret_key).encode("utf-8"), date_stamp)
        k_region = self.sign(k_date, self.region)
        k_service = self.sign(k_region, self.service)
        k_signing = self.sign(k_service, "aws4_request")
        return k_signing

    def add_auth(self, method, url, headers, body):
        t = datetime.datetime.utcnow()
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")
        parsed_url = requests.utils.urlparse(url)
        canonical_uri = parsed_url.path or "/"
        canonical_querystring = parsed_url.query

        payload_hash = hashlib.sha256(body or b"").hexdigest()

        canonical_headers = f"host:{parsed_url.netloc}\n" + f"x-amz-date:{amz_date}\n"
        signed_headers = "host;x-amz-date"

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
            f"{algorithm} Credential={self.access_key}/{credential_scope}, " f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        headers.update({"x-amz-date": amz_date, "Authorization": authorization_header, "host": parsed_url.netloc})


class BaseAmazonAMPStream:
    def __init__(self, config: dict):
        self.config = config
        self.auth = SigV4Authenticator(access_key=config["access_key"], secret_key=config["secret_key"], region=config["region"])
        self.base_url = f"https://aps-workspaces.{config['region']}.amazonaws.com/workspaces/{config['workspace_id']}"

    def request(self, path: str) -> dict:
        url = self.base_url + path
        method = "GET"
        headers = {}
        body = b""

        self.auth.add_auth(method, url, headers, body)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


class MetricNamesStream(BaseAmazonAMPStream):
    def read_records(self) -> Iterable[dict]:
        data = self.request("/api/v1/label/__name__/values")
        for metric in data.get("data", []):
            yield {"metric_name": metric}


class RulesStream(BaseAmazonAMPStream):
    def read_records(self) -> Iterable[dict]:
        data = self.request("/api/v1/rules")
        groups = data.get("data", {}).get("groups", [])
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                yield {
                    "name": rule.get("name"),
                    "state": rule.get("state"),
                    "query": rule.get("query"),
                    "duration": rule.get("duration"),
                    "keepFiringFor": rule.get("keepFiringFor"),
                    "system": rule.get("labels", {}).get("system"),
                    "severity": rule.get("labels", {}).get("severity"),
                    "description": rule.get("annotations", {}).get("description"),
                    "runbook": rule.get("annotations", {}).get("runbook"),
                    "summary": rule.get("annotations", {}).get("summary"),
                    "health": rule.get("health"),
                    "lastError": rule.get("lastError"),
                    "type": rule.get("type"),
                    "lastEvaluation": rule.get("lastEvaluation"),
                    "evaluationTime": rule.get("evaluationTime"),
                    "labels": rule.get("labels", {}),
                    "annotations": rule.get("annotations", {}),
                    "alerts": rule.get("alerts", []),
                }


class SourceAmazonAMP(Source):
    def __init__(self):
        self.logger = init_logger("source_amazon_amp")

    def check(self, logger, config) -> AirbyteConnectionStatus:
        try:
            stream = MetricNamesStream(config)
            next(stream.read_records())
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}", exc_info=True)
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))

    def discover(self, logger, config) -> AirbyteCatalog:
        streams = [
            AirbyteStream(
                name="MetricNames",
                json_schema={
                    "type": "object",
                    "properties": {"metric_name": {"type": ["string", "null"]}},
                    "additionalProperties": True,
                },
                supported_sync_modes=[SyncMode.full_refresh],
            ),
            AirbyteStream(
                name="Rules",
                json_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": ["string", "null"]},
                        "state": {"type": ["string", "null"]},
                        "query": {"type": ["string", "null"]},
                        "duration": {"type": ["integer", "null"]},
                        "keepFiringFor": {"type": ["integer", "null"]},
                        "system": {"type": ["string", "null"]},
                        "severity": {"type": ["string", "null"]},
                        "description": {"type": ["string", "null"]},
                        "runbook": {"type": ["string", "null"]},
                        "summary": {"type": ["string", "null"]},
                        "health": {"type": ["string", "null"]},
                        "lastError": {"type": ["string", "null"]},
                        "type": {"type": ["string", "null"]},
                        "lastEvaluation": {"type": ["string", "null"]},
                        "evaluationTime": {"type": ["number", "null"]},
                        "labels": {
                            "type": ["object", "null"],
                            "properties": {"severity": {"type": ["string", "null"]}, "system": {"type": ["string", "null"]}},
                            "additionalProperties": True,
                        },
                        "annotations": {
                            "type": ["object", "null"],
                            "properties": {
                                "description": {"type": ["string", "null"]},
                                "runbook": {"type": ["string", "null"]},
                                "summary": {"type": ["string", "null"]},
                            },
                            "additionalProperties": True,
                        },
                        "alerts": {"type": "array", "items": {"type": "object"}},
                    },
                    "additionalProperties": True,
                },
                supported_sync_modes=[SyncMode.full_refresh],
            ),
        ]
        return AirbyteCatalog(streams=streams)

    def streams(self, config) -> list:
        return [MetricNamesStream(config), RulesStream(config)]

    def read(self, logger, config, configured_catalog, state=None):
        from datetime import datetime

        for configured_stream in configured_catalog.streams:
            stream_name = configured_stream.stream.name
            if stream_name == "MetricNames":
                stream = MetricNamesStream(config)
            elif stream_name == "Rules":
                stream = RulesStream(config)
            else:
                continue

            for record in stream.read_records():
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=stream_name, data=record, emitted_at=int(datetime.now().timestamp() * 1000)),
                )

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/sources/amazon-amp",
            connectionSpecification={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "title": "Amazon AMP Source Spec",
                "required": ["workspace_id", "region", "access_key", "secret_key"],
                "properties": {
                    "workspace_id": {"type": "string", "description": "ID of the AMP workspace", "title": "AMP Workspace ID", "order": 0},
                    "region": {
                        "type": "string",
                        "enum": [
                            "af-south-1",
                            "ap-east-1",
                            "ap-northeast-1",
                            "ap-northeast-2",
                            "ap-northeast-3",
                            "ap-south-1",
                            "ap-south-2",
                            "ap-southeast-1",
                            "ap-southeast-2",
                            "ap-southeast-3",
                            "ap-southeast-4",
                            "ca-central-1",
                            "ca-west-1",
                            "cn-north-1",
                            "cn-northwest-1",
                            "eu-central-1",
                            "eu-central-2",
                            "eu-north-1",
                            "eu-south-1",
                            "eu-south-2",
                            "eu-west-1",
                            "eu-west-2",
                            "eu-west-3",
                            "il-central-1",
                            "me-central-1",
                            "me-south-1",
                            "sa-east-1",
                            "us-east-1",
                            "us-east-2",
                            "us-gov-east-1",
                            "us-gov-west-1",
                            "us-west-1",
                            "us-west-2",
                        ],
                        "default": "eu-central-1",
                        "description": "AWS region where AMP is deployed",
                        "title": "AWS Region",
                        "order": 1,
                    },
                    "access_key": {
                        "type": "string",
                        "description": "The Access Key ID of the AWS IAM Role with AMP access",
                        "title": "AWS IAM Access Key ID",
                        "airbyte_secret": True,
                        "order": 2,
                    },
                    "secret_key": {
                        "type": "string",
                        "description": "The Secret Key of the AWS IAM Role with AMP access",
                        "title": "AWS IAM Secret Key",
                        "airbyte_secret": True,
                        "order": 3,
                    },
                },
                "additionalProperties": True,
            },
        )

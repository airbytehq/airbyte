from typing import Any, List, Mapping, Tuple
import boto3
import logging

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from source_cloudwatch_logs.streams import Logs


# Source
class SourceCloudwatchLogs(AbstractSource):
    @staticmethod
    def _assume_role_session(config: Mapping[str, Any]) -> boto3.Session:
        """
        Uses STS to assume the role specified in config['role_arn']
        """
        base_session = boto3.Session(
            region_name=config["region_name"],
            aws_access_key_id=config.get("aws_access_key_id"),
            aws_secret_access_key=config.get("aws_secret_access_key"),
        )

        if not config.get("role_arn"):
            return base_session

        sts_client = base_session.client("sts")
        assumed_role = sts_client.assume_role(
            RoleArn=config["role_arn"],
            RoleSessionName="airbyte-cloudwatch-session",
            DurationSeconds=config.get("role_session_duration", 3600),
        )

        credentials = assumed_role["Credentials"]
        session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
            region_name=config["region_name"],
        )
        return session

    def check_connection(
        self, logger: logging.Logger, config: Mapping[str, Any]
    ) -> Tuple[bool, Any]:
        """
        Checks the authentication to AWS
        :param logger: airbyte logger
        :param config: connector configuration
        :return:
        """
        try:
            session = self._assume_role_session(config)
            client = session.client("logs")
            if config.get("log_group_prefix"):
                # Validate specific log group
                client.describe_log_streams(
                    logGroupPrefix=config["log_group_prefix"]
                )
            else:
                # Validate access to at least some log groups
                client.describe_log_groups(limit=1)
            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _get_log_group_names(
        config: Mapping[str, Any], session: boto3.Session
    ) -> List[str]:
        client = session.client("logs")

        groups = []
        paginator = client.get_paginator("describe_log_groups")
        prefix = config.get("log_group_prefix")
        pagination_kwargs = {"logGroupNamePrefix": prefix} if prefix else {}

        for page in paginator.paginate(**pagination_kwargs):
            for group in page.get("logGroups", []):
                groups.append(group["logGroupName"])

        return groups

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        session = self._assume_role_session(config)
        region = config["region_name"]
        log_groups = self._get_log_group_names(config, session)

        streams: List = [
            Logs(region_name=region, log_group_name=group, session=session)
            for group in log_groups
        ] + [
            Logs(
                region_name=region,
                session=session,
                name=custom["name"],
                log_group_name=custom["log_group_name"],
                log_stream_names=custom.get("log_stream_names"),
                filter_pattern=custom.get("filter_pattern"),
            )
            for custom in config.get("custom_log_reports", [])
        ]

        return streams

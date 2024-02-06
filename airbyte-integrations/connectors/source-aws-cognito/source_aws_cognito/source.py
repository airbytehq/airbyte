#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import boto3
import pkgutil
import os
from datetime import datetime
from typing import Dict, Generator

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    SyncMode,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream

schema_json = {
  "$schema": "http://json-schema.org/draft-07/schema",
  "type": ["null", "object"],
  "properties": {
    "Username": {
      "type": ["null", "string"]
    },
    "UserCreateDate": {
      "type": ["null", "date-time"]
    },
    "UserLastModifiedDate": {
      "type": ["null", "date-time"]
    },
    "Enabled": {
      "type": ["null", "boolean"]
    },
    "UserStatus": {
      "type": ["null", "string"]
    },
    "Attributes": {
      "type": ["null", "array"],
      "items": {
        "type": "object",
        "properties": {
          "Name": {
            "type": ["null", "string"]
          },
          "Value": {
            "type": ["null", "string", "number"]
          }
        }
      }
    }
  }
}
    


class SourceAwsCognito(Source):
    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration
            e.g: if a provided Stripe API token can be used to connect to the Stripe API.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            client = self._get_client(config, logger)
            
            client.list_user_pools(MaxResults=1)

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def _get_user_groups(self, cognito, user_pool_id, schema):
        streams = []
        next_page = None
        pages_remain = True
        kwargs = {
            "UserPoolId":user_pool_id
        }
        
        while(pages_remain):
            if next_page:
                kwargs['NextToken'] = next_page
            response = cognito.list_groups(**kwargs)
            for group in response['Groups']:
                group_name = group['GroupName']
                stream_name = user_pool_id + '_group_' + group_name
                streams.append(AirbyteStream(name=stream_name, json_schema=schema, supported_sync_modes=[SyncMode.full_refresh], source_defined_cursor=False))
            next_page = response.get('NextToken', None)
            pages_remain = next_page is not None
        
        return streams

    def _get_user_pools(self, cognito, schema):
        streams = []
        kwargs = {"MaxResults":50}
        next_page = None
        pages_remain = True
        while(pages_remain):
            if next_page:
                kwargs['NextToken'] = next_page
            response = cognito.list_user_pools(**kwargs)
            for pool in response['UserPools']:
                stream_name = pool['Name']
                streams.append(AirbyteStream(name=pool['Id'], json_schema=schema, supported_sync_modes=[SyncMode.full_refresh], source_defined_cursor=False))
                streams.extend(self._get_user_groups(cognito, pool['Id'], schema))
            next_page = response.get('NextToken', None)
            pages_remain = next_page is not None
        
        return streams

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        """
        Returns an AirbyteCatalog representing the available streams and fields in this integration.
        For example, given valid credentials to a Postgres database,
        returns an Airbyte catalog where each postgres table is a stream, and each table column is a field.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteCatalog is an object describing a list of all available streams in this source.
            A stream is an AirbyteStream object that includes:
            - its stream name (or table name in the case of Postgres)
            - json_schema providing the specifications of expected schema for this stream (a list of columns described
            by their names and types)
        """

        try:
            client = self._get_client(config, logger)

            streams = self._get_user_pools(client, schema_json)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")
        
        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        """
        Returns a generator of the AirbyteMessages generated by reading the source with the given configuration,
        catalog, and state.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
            the properties of the spec.yaml file
        :param catalog: The input catalog is a ConfiguredAirbyteCatalog which is almost the same as AirbyteCatalog
            returned by discover(), but
        in addition, it's been configured in the UI! For each particular stream and field, there may have been provided
        with extra modifications such as: filtering streams and/or columns out, renaming some entities, etc
        :param state: When a Airbyte reads data from a source, it might need to keep a checkpoint cursor to resume
            replication in the future from that saved checkpoint.
            This is the object that is provided with state from previous runs and avoid replicating the entire set of
            data everytime.

        :return: A generator that produces a stream of AirbyteRecordMessage contained in AirbyteMessage object.
        """
        
        client = self._get_client(config, logger)
        logger.info(f"Starting syncing {self.__class__.__name__}")
        for configured_stream in catalog.streams:
            stream = configured_stream.stream
            stream_name = stream.name
            kwargs = {"UserPoolId": stream.name}
            list_user_function = client.list_users
            next_token_str = "PaginationToken"

            # Deal with groups
            group_name = None
            if "_group_" in stream.name:
                stream_name_s = stream.name.split("_group_",1)
                pool_id = stream_name_s[0]
                group_name = stream_name_s[1]
                list_user_function = client.list_users_in_group
                kwargs["UserPoolId"] = pool_id
                kwargs['GroupName'] = group_name
                next_token_str = "NextToken"
        

            next_page = None
            users_remain = True
            while(users_remain):
                if next_page:
                    kwargs[next_token_str] = next_page
                response = list_user_function(**kwargs)
                for user in response['Users']:
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(stream=stream_name, data=user, emitted_at=int(datetime.now().timestamp()) * 1000),
                    )
                next_page = response.get(next_token_str, None)
                users_remain = next_page is not None
                
        logger.info(f"Finished syncing {self.__class__.__name__}")

    def _get_client(self, config, logger):
        cognito_region = config["region"]
        logger.debug("Amazon Cognito Source Config Check - region: " + cognito_region)
        # Senstive Properties
        access_key = config["access_key"]
        logger.debug("Amazon Cognito Source Config Check - access_key (ends with): " + access_key[-1])
        secret_key = config["secret_key"]
        logger.debug("Amazon Cognito Source Config Check - secret_key (ends with): " + secret_key[-1])

        logger.debug("Amazon Cognito Source Config Check - Starting connection test ---")
        return boto3.client("cognito-idp", aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=cognito_region)

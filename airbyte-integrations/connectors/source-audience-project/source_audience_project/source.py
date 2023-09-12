#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from .auth import AudienceProjectAuthenticator
from .streams import AudienceProjectStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from .streams import Campaigns


# Declarative Source
class SourceAudienceProject(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})


# # Declarative Source
# class SourceAudienceProjectYaml(YamlDeclarativeSource, AbstractSource):
#     def __init__(self):
#         super().__init__(**{"path_to_yaml": "manifest.yaml"})
#
#
# # Source
# class SourceAudienceProject(SourceAudienceProjectYaml):
#
#     def check_connection(self, logger, config) -> Tuple[bool, any]:
#         authenticator = self._make_authenticator(config)
#         try:
#             # Checking campaign stream as a check method.
#             campaign_stream = Campaigns(authenticator, config)
#             next(campaign_stream.read_records(SyncMode.full_refresh))
#             return True, None
#         except Exception as e:
#             return False, e
#
#     @staticmethod
#     def _make_authenticator(config: Mapping[str, Any]):
#         # Return Auth header with the bearer token in both conditions.
#         if config["credentials"]["type"] == "access_token":
#             return TokenAuthenticator(token=config["credentials"]["access_token"])
#         else:
#             return AudienceProjectAuthenticator(
#                 url_base=AudienceProjectStream.oauth_url_base,
#                 config=config
#             )
#
#     def streams(self, config: Mapping[str, Any]) -> List[Stream]:
#         auth = self._make_authenticator(config)
#         return [
#             Campaigns(authenticator=auth, config=config),
#         ]

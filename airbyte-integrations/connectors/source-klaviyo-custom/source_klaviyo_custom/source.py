from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from source_klaviyo_custom.streams import (
    KlaviyoCustomStream
    , KlaviyoAuthenticator
    , Lists
    , ListMembers
    , ListExclusions
    , Profiles
)

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

# Source
class SourceKlaviyoCustom(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        url = "https://a.klaviyo.com/api/v2/lists"
        try:
            r = requests.get(url,auth=KlaviyoAuthenticator(config["api_key"]))

            if r.status_code == 200:
                return True,None
            else:
                error = r.text
                logger.error(error)
                return False, error
        
        except Exception as e:
            logger.exception(e)
            return False,e


    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        
        auth = KlaviyoAuthenticator(config["api_key"])
        list_members_stream = ListMembers(config["list_id"],authenticator=auth)
        list_exclusions_stream = ListExclusions(config["list_id"],authenticator=auth)
        profiles_stream = Profiles(exclude_list=list_exclusions_stream,parent=list_members_stream,authenticator=auth)
        
        return [
            list_members_stream
            ,list_exclusions_stream
            ,profiles_stream
        ]

d=1
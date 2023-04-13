#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from .stream_follower_details import FollowerDetails
from .stream_user_detail import UserDetail
from .stream_tweet_metrics import TwitterTweetMetrics


class SourceTwitterMetrics(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        api_key = config["api_key"]
        screen_name = config["screen_name"]
        if api_key and screen_name:
            return True, None
        else:
            return False, "Api key of Screen Name should not be null!"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Replace the streams below with your own streams.
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # remove the authenticator if not required.
        print("config \n", config)
        auth = TokenAuthenticator(token=config["api_key"])  # Oauth2Authenticator is also available if you need oauth support
        print("auth \n", auth.get_auth_header())
        return [
            UserDetail(authenticator=auth, config=config),
            TwitterTweetMetrics(authenticator=auth, config=config),
            FollowerDetails(authenticator=auth, config=config)
        ]

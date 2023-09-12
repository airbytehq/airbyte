#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import logging
from typing import Any, List, Mapping, Optional, Tuple
from datetime import datetime, timedelta

import pendulum
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from .schemas import Profile
from .streams import (
    Profiles,
    AirbytePurchasedProductSp,
    AirbyteAdvertisedProductSp,
    AirbyteSearchTermSp,
    AirbyteTargetingSp,
    AirbyteCampPlacementSp,
    AirbyteCampAdgroupsSp,
    AirbyteCampSp,
    AirbyteSearchTermLastMonthSp,
    AirbytePurchasedProductLastMonthSp, 
    AirbyteAdvertisedProductLastMonthSp, 
    AirbyteCampLastMonthSp, 
    AirbyteCampAdgroupsLastMonthSp, 
    AirbyteCampPlacementLastMonthSp, 
    AirbyteTargetingLastMonthSp
)

# Oauth 2.0 authentication URL for amazon
TOKEN_URL = "https://api.amazon.com/auth/o2/token"
CONFIG_DATE_FORMAT = "YYYY-MM-DD"

#self._session.verify = False
class SourceAmazonAds(AbstractSource):

    def _validate_and_transform(self, config: Mapping[str, Any]):

        customer_id = config.get("customer_id") if config.get("customer_id",None) else "NA"
        logger = logging.getLogger("airbyte")
        start_date = config.get("start_date")
        end_date = config.get("end_date")
        if start_date:
            config["start_date"] = pendulum.from_format(start_date, CONFIG_DATE_FORMAT).date()
        else:
            config["start_date"] = None
        if end_date:
            config["end_date"] = pendulum.from_format(end_date, CONFIG_DATE_FORMAT).date()
        else:
            config["end_date"] = None
        if not config.get("region"):
            source_spec = self.spec(logger)
            config["region"] = source_spec.connectionSpecification["properties"]["region"]["default"]
        if not config.get("look_back_window"):
            source_spec = self.spec(logger)
            config["look_back_window"] = 0 #source_spec.connectionSpecification["properties"]["look_back_window"]["default"]
        config["report_record_types"] = config.get("report_record_types", [])
        return config

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            config = self._validate_and_transform(config)
        except Exception as e:
            return False, str(e)
        # Check connection by sending list of profiles request. Its most simple
        # request, not require additional parameters and usually has few data
        # in response body.
        # It doesnt support pagination so there is no sense of reading single
        # record, it would fetch all the data anyway.
        Profiles(config, authenticator=self._make_authenticator(config)).get_all_profiles()
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        :return list of streams for current source
        """
        try:
            config = self._validate_and_transform(config)
            auth = self._make_authenticator(config)
            stream_args = {"config": config, "authenticator": auth}
            config["last_month"] = True
            last_month_stream_args = {"config": config, "authenticator": auth}
            # All data for individual Amazon Ads stream divided into sets of data for
            # each profile. Every API request except profiles has required
            # paramater passed over "Amazon-Advertising-API-Scope" http header and
            # should contain profile id. So every stream is dependant on Profiles
            # stream and should have information about all profiles.
            print("Abhinandan---------------")

            print("Abhinandan---------------",config)

            profiles_stream = Profiles(**stream_args)
            profiles_list = profiles_stream.get_all_profiles()
            print("Abhinandan---------------",profiles_list)

            stream_args["profiles"] = self._choose_profiles(config, profiles_list)
            last_month_stream_args["profiles"] = self._choose_profiles(config, profiles_list)
            print("Abhinandan---stream_args------------",profiles_list)
            
            non_profile_stream_classes = [
                AirbyteCampSp,
                AirbyteCampAdgroupsSp,
                AirbyteCampPlacementSp,
                AirbyteTargetingSp,
                AirbyteSearchTermSp,
                AirbyteAdvertisedProductSp,
                AirbytePurchasedProductSp,
                AirbyteSearchTermLastMonthSp,
                AirbytePurchasedProductLastMonthSp, 
                AirbyteAdvertisedProductLastMonthSp, 
                AirbyteCampLastMonthSp, 
                AirbyteCampAdgroupsLastMonthSp, 
                AirbyteCampPlacementLastMonthSp, 
                AirbyteTargetingLastMonthSp
            ]
            last_month_stream_classes = [AirbyteSearchTermLastMonthSp,
                                        AirbytePurchasedProductLastMonthSp, 
                                        AirbyteAdvertisedProductLastMonthSp, 
                                        AirbyteCampLastMonthSp, 
                                        AirbyteCampAdgroupsLastMonthSp, 
                                        AirbyteCampPlacementLastMonthSp, 
                                        AirbyteTargetingLastMonthSp]
            #non_profile_stream_classes = [SponsoredDisplayCampaigns,SponsoredDisplayAdGroups,SponsoredBrandsVideoReportStream]
            return [profiles_stream, *[stream_class(**stream_args) if stream_class not in last_month_stream_classes else stream_class(**last_month_stream_args) for stream_class in non_profile_stream_classes]]
        except Exception as ex:
            self.logger.exception(f"Encountered an exception while reading stream {ex}")
            raise ex



    @staticmethod
    def _make_authenticator(config: Mapping[str, Any]):
        return Oauth2Authenticator(
            token_refresh_endpoint=TOKEN_URL,
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )

    @staticmethod
    def _choose_profiles(config: Mapping[str, Any], profiles: List[Profile]):
        if not config.get("profiles"):
            return profiles
        return list(filter(lambda profile: profile.profileId in config["profiles"], profiles))

    def __del__(self):
        pass

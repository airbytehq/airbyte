#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib import request

import requests

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .authenticator import AppleSearchAdsAuthenticator

from .basic_streams import Campaigns
from .with_campaign_streams import Adgroups, CampaignNegativeKeywords, CreativeSets, AdgroupCreativeSets
from .with_campaign_report_streams import ReportCampaigns

class SourceAppleSearchAds(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = AppleSearchAdsAuthenticator(
            client_id=config["client_id"],
            team_id=config["team_id"],
            key_id=config["key_id"],
            private_key=config["private_key"]
        )

        try:
            logger.info("Apple Search Ads me access")
            response = requests.request(
                "GET",
                url="https://api.searchads.apple.com/api/v4/me",
                headers=auth.get_auth_header()
            )

            if response.status_code != 200:
                message = response.json()
                error_message = message.get("error")
                if error_message:
                    return False, error_message
                response.raise_for_status()
        except Exception as e:
            logger.info(f"Apple Search Ads failed {e}")
            return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = AppleSearchAdsAuthenticator(
            client_id=config["client_id"],
            team_id=config["team_id"],
            key_id=config["key_id"],
            private_key=config["private_key"]
        )

        return [
            Campaigns(org_id=config["org_id"], authenticator=auth),
            Adgroups(org_id=config["org_id"], authenticator=auth),
            CampaignNegativeKeywords(org_id=config["org_id"], authenticator=auth),
            CreativeSets(org_id=config["org_id"], authenticator=auth),
            AdgroupCreativeSets(org_id=config["org_id"], authenticator=auth),
            ReportCampaigns(org_id=config["org_id"], authenticator=auth)
        ]

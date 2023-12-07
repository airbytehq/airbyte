#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from source_ironsource.authenticator import RenewalSecretKeyAuthenticator
from source_ironsource.streams import Creatives, Campaigns, CampaignCreatives, Assets, Titles, Bids, CountryGroups, CampaignTargetings

DEFAULT_PAGE_SIZE = 500


# Basic full refresh stream
class SourceIronsource(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = RenewalSecretKeyAuthenticator(secret_key=config["secret_key"], refresh_token=config["refresh_token"]).get_auth_header()

            response = requests.get(f"https://api.ironsrc.com/advertisers/v4/campaigns", headers=auth)
            response.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = {
            "page_size": int(config.get("page_size", DEFAULT_PAGE_SIZE)),
            "authenticator": RenewalSecretKeyAuthenticator(secret_key=config["secret_key"], refresh_token=config["refresh_token"])
        }
        campaigns_stream = Campaigns(**args)
        return [
            Assets(**args),
            Bids(campaigns_stream=campaigns_stream, **args),
            campaigns_stream,
            CampaignTargetings(campaigns_stream=campaigns_stream, **args),
            CampaignCreatives(campaigns_stream=campaigns_stream, **args),
            CountryGroups(campaigns_stream=campaigns_stream, **args),
            Creatives(**args),
            Titles(**args)
        ]

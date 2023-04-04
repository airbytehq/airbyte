#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from datetime import datetime
from collections import Counter

import pendulum
import requests
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from requests_oauthlib import OAuth1
from source_netsuite2.constraints import INCREMENTAL_CURSOR, RECORD_PATH, REST_PATH
from source_netsuite2.streams import InventorySnapshot, Transactions


# Source
class SourceNetsuite2(AbstractSource):

    logger: logging.Logger = logging.getLogger("airbyte")

    def auth(self, config: Mapping[str, Any]) -> OAuth1:
        # the `realm` param should be in format of: 12345_SB1
        realm = config["realm"].replace("-", "_").upper()
        return OAuth1(
            client_key=config["consumer_key"],
            client_secret=config["consumer_secret"],
            resource_owner_key=config["token_key"],
            resource_owner_secret=config["token_secret"],
            realm=realm,
            signature_method="HMAC-SHA256",
        )

    def base_url(self, config: Mapping[str, Any]) -> str:
        # the subdomain should be in format of: 12345-sb1
        subdomain = config["realm"].replace("_", "-").lower()
        return f"https://{subdomain}.suitetalk.api.netsuite.com"

    def get_session(self, auth: OAuth1) -> requests.Session:
        session = requests.Session()
        session.auth = auth
        return session
    
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        auth = self.auth(config)
        base_url = self.base_url(config)
        session = self.get_session(auth)  
        url = base_url + RECORD_PATH + "contact"
        logger.info(f"Checking connection with {url}")
        try:
            response = session.get(url=url, params={"limit": 1})
            response.raise_for_status()
            return True, None
        except requests.exceptions.HTTPError as e:
                return False, e
    

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.auth(config)
        session = self.get_session(auth)
        base_url = self.base_url(config)
        object_names = config.get("object_types") or ["SalesOrd","ItemRcpt","ItemShip","CashSale","PurchOrd","CustPymt","CustInvc","CustRfnd","CustCred","InvTrnfr","InvAdjst"]


        input_args = {
            "auth": auth,
            "base_url": base_url,
            "start_datetime": config["start_datetime"],
            "window_in_days": config["window_in_days"],
            "object_names": object_names,
        }
        return [Transactions(**input_args),InventorySnapshot(**input_args)]

#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from multiprocessing import AuthenticationError
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from source_toantest.streams import Historical,ToantestAuthenticator,Latest,datetime


# Source
class SourceToantest(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        check_url = "http://api.exchangeratesapi.io/v1/latest"
        try:
            response = requests.get(check_url,auth=ToantestAuthenticator(config["access_key"]))
            if response.status_code == 200:
                return True, None
            else:
                raise ValueError(f"Response not success. Response: {response.text}")
        except Exception as e:
            logger.error(e)
            return False, e


    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        
        auth = ToantestAuthenticator(config["access_key"])
        # start_date: str = config["start_date"]
        start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')

        return [Latest(authenticator=auth),Historical(authenticator=auth,start_date=start_date)]

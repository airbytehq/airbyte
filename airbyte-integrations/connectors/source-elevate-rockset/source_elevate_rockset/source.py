#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
import requests
from .streams import Workspace_new


class SourceElevateRockset(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            url_2 = "https://{}.rockset.com/v1/orgs/self/ws/".format(
                config["region_url"])
            url_list = url_2 + config["workspace"] + "/collections"
            print(url_list)
            payload = {}
            headers = {
                'Authorization': 'ApiKey {}'.format(config["api_token"])
            }

            response = requests.request(
                "GET", url_list, headers=headers, data=payload)

            status = response.status_code
            logger.info(f"Ping response code: {status}")
            if status == 200:
                return True, None
        except Exception as e:
            return False, f"Please check that your API key and workspace name are entered correctly: {repr(e)}"

    def lambdanew(self, config):

        url_2 = "https://{}.rockset.com/v1/orgs/self/ws/".format(
            config["region_url"])
        url_list = url_2 + config["workspace"] + "/collections"
        print(url_list)
        payload = {}
        headers = {
            'Authorization': 'ApiKey {}'.format(config["api_token"])
        }

        response = requests.request(
            "GET", url_list, headers=headers, data=payload)
        print("#######################################")
        print(url_list)
        jsondata = response.json()
        print(jsondata)
        streams = []
        for i in range(len(jsondata['data'])):
            streams.append(jsondata['data'][i]["name"])
        print("this is the stream value", streams)

        table_lists = streams
        for table in table_lists:
            stream_kwargs = {
                "authenticator": TokenAuthenticator(config["api_token"], auth_header="Authorization", auth_method="ApiKey"),
                "workspace": config["workspace"],
                "name": table,
                "api_token": config["api_token"],
                "start_date": config['start_date'],
                "region_url": config['region_url']

            }
            yield Workspace_new(**stream_kwargs)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        var = self.lambdanew(config)
        return var

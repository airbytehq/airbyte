#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

from .auth import CredentialsCraftAuthenticator
from .utils import chunks, date_to_timestamp, get_today_minus_n_days_date, get_yesterday_date, xor


# Basic full refresh stream
class VkAdsStream(HttpStream, ABC):
    url_base = "https://api.vk.com/method/"
    transformer: TypeTransformer = TypeTransformer(
        config=TransformConfig.DefaultSchemaNormalization)

    def __init__(
        self,
        auth: TokenAuthenticator,
        account_type,
        client_id,
        account_id,
        date_from,
        date_to,
        last_days,
        client_name='',
        product_name='',
        custom_json={},
        include_deleted=1,
    ):
        HttpStream.__init__(self, authenticator=None)
        self.access_token = auth._token
        self.account_type = account_type
        self.client_id = client_id
        self.account_id = account_id
        self.date_from = date_from
        self.date_to = date_to
        self.last_days = last_days
        self.client_name = client_name
        self.product_name = product_name
        self.custom_json = custom_json
        self.include_deleted = include_deleted

    def next_page_token(self, *args, **kwargs) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {
            'access_token': self.access_token,
            'v': '5.131',
            'account_id': self.account_id
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        print('URL', response.request.url)
        try:
            yield from map(self.add_constants_to_record, data['response'])
        except Exception as e:
            raise Exception(f"{e}; Response data: {str(data)}")

    def add_extra_properties_to_schema(self, schema):
        extra_properties = ["__productName", "__clientName"]
        custom_keys = self.custom_json.keys()
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}
        return schema

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        return self.add_extra_properties_to_schema(schema)

    def add_constants_to_record(self, record):
        constants = {
            "__productName": self.product_name,
            "__clientName": self.client_name,
        }
        constants.update(self.custom_json)
        record.update(constants)
        return record

    def should_retry(self, response: requests.Response) -> bool:
        should_retry_ = super().should_retry(response)
        data = response.json()
        if data.get('error_code'):
            error = data
        else:
            error = data.get('error')
        if not error:
            return should_retry_
        else:
            self.logger.warning(f"API Error: {response.text}")
        should_retry_error_codes = [1, 6, 9, 10, 29, 603, 601]
        return error['error_code'] in should_retry_error_codes or should_retry_


class ObjectStream(VkAdsStream, ABC):
    use_cache = True
    primary_key = 'id'

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(*args, **kwargs)
        if self.account_type == 'Agency':
            params.update(
                {'client_id': self.client_id}
            )
        params['include_deleted'] = self.include_deleted
        return params


class Campaigns(ObjectStream):

    def path(self, *args, **kwargs) -> str:
        return 'ads.getCampaigns'


class Ads(ObjectStream, HttpSubStream):
    limit = 2000
    def __init__(
        self,
        auth: TokenAuthenticator,
        account_type,
        client_id,
        account_id,
        date_from,
        date_to,
        last_days,
        parent_stream_instance: Campaigns,
        client_name='',
        product_name='',
        custom_json={},
        include_deleted=1,
    ):
        HttpSubStream.__init__(self, parent=parent_stream_instance)
        ObjectStream.__init__(
            self,
            auth=auth,
            account_type=account_type,
            client_id=client_id,
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            last_days=last_days, 
            client_name=client_name, 
            product_name=product_name,
            custom_json=custom_json,
            include_deleted=include_deleted
        )
        self.current_offset = 0

    def path(self, *args, **kwargs) -> str:
        return 'ads.getAds'
    
    def next_page_token(self, response: requests.Response, **kwargs) -> Optional[Mapping[str, Any]]:
        if len(response.json()['response']) >= self.limit:
            self.current_offset += self.limit
            return {"offset": self.current_offset}
        
        else:
            self.current_offset = 0
            return None
    
    def request_params(self, next_page_token: Mapping[str, Any], stream_slice: Mapping[str, Any], *args, **kwargs) -> MutableMapping[str, Any]:
        next_page_token = {} if not next_page_token else next_page_token
        return {
            **super().request_params(*args, **kwargs),
            "limit": self.limit,
            "offset": 0 or next_page_token.get("offset"),
            "campaign_ids": json.dumps([int(stream_slice["parent"]["id"])]),
            "ad_ids": None,
        }


class ObjectStatisticsMixin(VkAdsStream, HttpSubStream, ABC):
    primary_key = "id"
    stat_obj_type = ''
    parent_stream_class: VkAdsStream = None

    def __init__(self,
                 *args, **kwargs
                 ):
        VkAdsStream.__init__(
            self,
            *args, **kwargs
        )
        HttpSubStream.__init__(
            self,
            self.parent_stream_class(
                *args, **kwargs
            )
        )

    def path(self, *args, **kwargs) -> str:
        return "ads.getStatistics"

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = ResourceSchemaLoader(package_name_from_class(
            self.__class__)).get_schema('statistics')
        schema["properties"][self.stat_obj_type +
                             '_id'] = schema["properties"]['id']
        del schema["properties"]['id']
        return self.add_extra_properties_to_schema(schema)

    def request_params(self, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> MutableMapping[str, Any]:
        params = VkAdsStream.request_params(
            self, stream_slice, *args, **kwargs)
        params.update({
            'ids_type': self.stat_obj_type,
            'ids': ','.join(stream_slice),
            'period': 'day',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        try:
            data = response.json()['response']
        except:
            raise Exception(str(response.text))
        for obj in data:
            for stat in obj['stats']:
                stat.update({
                    self.stat_obj_type + '_id': obj['id'],
                    'type': obj['type']
                })
                yield self.add_constants_to_record(stat)

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_records_ids = [
            str(record['parent']['id'])
            for record
            in HttpSubStream.stream_slices(self, *args, **kwargs)
        ]
        slices = list(chunks(parent_records_ids, 20))
        return slices


class AdsStatistics(ObjectStatisticsMixin):
    stat_obj_type = 'ad'
    parent_stream_class = Ads

    def __init__(self, parent_stream_instance: Ads, *args, **kwargs):
        VkAdsStream.__init__(
            self,
            *args, **kwargs
        )

        HttpSubStream.__init__(
            self,
            parent=parent_stream_instance
        )


class CampaignStatistics(ObjectStatisticsMixin):
    stat_obj_type = 'campaign'
    parent_stream_class = Campaigns


class AdsLayout(Ads):
    primary_key = "id"

    def path(self, *args, **kwargs) -> str:
        return 'ads.getAdsLayout'

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            stories = record.get('stories_data', {}).get("stories", [])
            for story in stories:
                story['story_type'] = story.pop('type')
            yield record


class SourceVkAds(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        config = SourceVkAds.get_updated_default_config(config)
        if xor(config['date_from'], config['date_to']) or (config['date_from'] and config['date_to'] and config['last_days']):
            return False, 'You must specify either Date From and Date To or just Last Days'

        if config['date_from'] and config['date_to']:
            if date_to_timestamp(config['date_from']) > date_to_timestamp(config['date_to']):
                return False, 'Date From is more than Date To'

        if config['account_type'] == 'Client' and config.get('client_id'):
            return False, "Client IDs must be specified only for Agency Account Type. You must specify' \
            ' only Account ID you're using Client Account Type"

        try:
            json.loads(config['custom_json'])
        except:
            return False, 'Custom JSON invalid format'

        auth = self.get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            check_auth = auth.check_connection()
            if not check_auth[0]:
                return check_auth

        params = {'access_token': auth._token, 'v': '5.131'}

        accounts_url = 'https://api.vk.com/method/ads.getAccounts'
        accounts_resp = requests.get(accounts_url, params=params).json()

        if accounts_resp.get('error'):
            return False, 'API error: ' + accounts_resp['error']['error_msg']

        accounts_ids = [str(acc['account_id'])
                        for acc in accounts_resp['response']]

        if config['account_id'] not in accounts_ids:
            return False, 'Account Id is invalid'

        if config['account_type'] == 'Agency':
            clients_url = 'https://api.vk.com/method/ads.getClients'
            params.update({'account_id': config['account_id']})
            clients_resp = requests.get(clients_url, params=params).json()

            if clients_resp.get('error'):
                return False, 'check ads.getClients API error: ' + clients_resp['error']['error_msg']

            clients_ids = [str(cl['id']) for cl in clients_resp['response']]

            if config.get('client_id') not in clients_ids:
                return False, 'Client Id is invalid'

        return True, None

    @staticmethod
    def get_updated_default_config(user_config):
        # To avoid Index Error in config dict
        default_config = {
            "auth": None,
            "account_type": "",
            "account_id": "",
            "client_id": "",
            "date_from": "",
            "date_to": "",
            "last_days": None,
            "client_name": '',
            "product_name": '',
            "custom_json": '{}',
            "include_deleted": True,
        }
        default_config.update(user_config)
        return default_config

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> TokenAuthenticator:
        if config["credentials"]["auth_type"] == "access_token_auth":
            return TokenAuthenticator(config["credentials"]["access_token"])
        elif config["credentials"]["auth_type"] == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception(
                "Invalid Auth type. Available: access_token_auth and credentials_craft_auth")

    @staticmethod
    def prepare_config(user_config: Mapping[str, Any]):
        config = SourceVkAds.get_updated_default_config(user_config)
        if not config.get("date_from") and not config.get("date_to"):
            config["date_from"] = (
                get_today_minus_n_days_date(config["last_days"])
                if config.get("last_days", 0) > 0
                else get_today_minus_n_days_date(30)
            )
            config["date_to"] = get_yesterday_date()

        config['custom_json'] = json.loads(config['custom_json'])
        config['auth'] = SourceVkAds.get_auth(config)
        config['include_deleted'] = int(config['include_deleted'])
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        prepared_config = self.prepare_config(config)
        del prepared_config['credentials']

        campaigns_stream_instance = Campaigns(**prepared_config)
        ads_stream_instance = Ads(
            **prepared_config,
            parent_stream_instance=campaigns_stream_instance
        )

        return [
            campaigns_stream_instance,
            ads_stream_instance,
            AdsLayout(**prepared_config, parent_stream_instance=campaigns_stream_instance),
            AdsStatistics(**prepared_config, parent_stream_instance=ads_stream_instance),
            CampaignStatistics(**prepared_config),
        ]

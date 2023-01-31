#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime, timedelta
import json
import logging
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from requests.auth import AuthBase
from source_smi2_mirtesen.auth import UsernamePasswordOauth2Authenticator
from source_smi2_mirtesen.models import RatesGranularity
from source_smi2_mirtesen.utils import dates_to_range
logger = logging.getLogger("airbyte")


# Basic full refresh stream
class Smi2MirtesenStream(HttpStream, ABC):
    transformer: TypeTransformer = TypeTransformer(
        config=TransformConfig.DefaultSchemaNormalization)
    url_base = "https://backend.media/api/v1/"
    primary_key = "id"
    limit = 1000

    def __init__(
        self,
        authenticator: Union[AuthBase, HttpAuthenticator],
        client_name_constant: str,
        product_name_constant: str,
        custom_constants: Dict[str, Any],
        filters: List[Any],
        agency_id: Optional[int] = None,
    ):
        HttpStream.__init__(self, authenticator=authenticator)
        self._authenticator = authenticator
        self.current_offset = 0
        self.client_name_constant = client_name_constant
        self.product_name_constant = product_name_constant
        self.custom_constants = custom_constants
        self.filters = filters
        self.agency_id = agency_id

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        items_len = len(response.json()["items"])
        if items_len > 0 and items_len == self.limit:
            self.current_offset += self.limit
            return {"offset": self.current_offset}
        else:
            self.current_offset = 0
            return None

    def add_extra_properties_to_schema(self, schema):
        extra_properties = ["__productName", "__clientName"]
        custom_keys = self.custom_constants.keys()
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}
        return schema

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        return self.add_extra_properties_to_schema(schema)

    def add_constants_to_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        constants = {
            "__productName": self.product_name_constant,
            "__clientName": self.client_name_constant,
        }
        constants.update(self.custom_constants)
        record.update(constants)
        return record

    def request_params(
        self, next_page_token: Mapping[str, Any] = None, *args, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {
            "limit": self.limit,
            "offset": next_page_token.get("offset") if next_page_token else 0
        }
        if self.filters:
            params["condition"] = json.dumps(self.filters)
        if self.agency_id:
            params["agencyId"] = self.agency_id
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        logger.info(
            f"Send request for stream {self.name}: URL: {response.request.url}; Headers: {response.request.headers}")
        yield from response.json()["items"]


class ObjectStream:
    def __init__(
        self,
        with_count: bool,
        with_rates: bool,
        rates_date_from: datetime,
        rates_date_to: datetime,
    ):
        self.with_count = with_count
        self.with_rates = with_rates
        self.rates_date_from = rates_date_from
        self.rates_date_to = rates_date_to

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        params = {
            "withCount": int(self.with_count),
            "withRates": int(self.with_rates),
            "ratesDates": dates_to_range(self.rates_date_from, self.rates_date_to),
        }
        return params


class Campaigns(Smi2MirtesenStream, ObjectStream):
    primary_key = "id"
    use_cache = True
    use_cache = True

    def __init__(
        self,
        authenticator: Union[AuthBase, HttpAuthenticator],
        client_name_constant: str,
        product_name_constant: str,
        custom_constants: Dict[str, Any],
        filters: List[Any],
        with_active_news_count: bool,
        with_connected_site_clicks: bool,
        with_count: bool,
        with_rates: bool,
        rates_date_from: datetime,
        rates_date_to: datetime,
        agency_id: Optional[str] = None,
    ):
        Smi2MirtesenStream.__init__(
            self,
            authenticator=authenticator,
            client_name_constant=client_name_constant,
            product_name_constant=product_name_constant,
            custom_constants=custom_constants,
            filters=filters,
            agency_id=agency_id,
        )
        ObjectStream.__init__(
            self,
            rates_date_from=rates_date_from,
            rates_date_to=rates_date_to,
            with_count=with_count,
            with_rates=with_rates,
        )
        self.with_active_news_count = with_active_news_count
        self.with_connected_site_clicks = with_connected_site_clicks

    def path(self, *args, **kwargs) -> str:
        return "campaigns"

    def request_params(
        self, *args, **kwargs
    ) -> MutableMapping[str, Any]:
        return {
            **Smi2MirtesenStream.request_params(self, *args, **kwargs),
            **ObjectStream.request_params(self, *args, **kwargs),
            "withActiveNewsCount": int(self.with_active_news_count),
            "withConnectedSiteClicks": int(self.with_connected_site_clicks),
        }


class ObjectRatesStream:
    def __init__(
        self,
        date_from: datetime,
        date_to: datetime,
        rates_granularity: RatesGranularity,
    ):
        self.date_from = date_from
        self.date_to = date_to
        self.rates_granularity = rates_granularity

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {
            "dates": dates_to_range(self.date_from, self.date_to),
            "groupBy": self.rates_granularity.value
        }


class CampaignsRates(Smi2MirtesenStream, ObjectRatesStream, HttpSubStream):
    primary_key = ["campaign_id", "date"]

    def __init__(
        self,
        authenticator: Union[AuthBase, HttpAuthenticator],
        client_name_constant: str,
        product_name_constant: str,
        custom_constants: Dict[str, Any],
        filters: List[Any],
        rates_granularity: RatesGranularity,
        date_from: datetime,
        date_to: datetime,
        campaigns_parent_stream: Campaigns,
        agency_id: Optional[int] = None,
    ):
        HttpSubStream.__init__(self, parent=campaigns_parent_stream)
        Smi2MirtesenStream.__init__(
            self,
            authenticator=authenticator,
            client_name_constant=client_name_constant,
            product_name_constant=product_name_constant,
            custom_constants=custom_constants,
            filters=filters,
            agency_id=agency_id,
        )
        ObjectRatesStream.__init__(
            self,
            date_from=date_from,
            date_to=date_to,
            rates_granularity=rates_granularity,
        )

    def build_condition(self, stream_slice: Mapping[str, Any] = None):
        if self.filters:
            return ['and', ["id", stream_slice["parent"]["id"]], self.filters]
        else:
            return ["id", stream_slice["parent"]["id"]]

    def request_params(self, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> MutableMapping[str, Any]:
        params = {
            **Smi2MirtesenStream.request_params(self, stream_slice=stream_slice, *args, **kwargs),
            **ObjectRatesStream.request_params(self, stream_slice=stream_slice, *args, **kwargs),
            "condition": json.dumps(self.build_condition(stream_slice=stream_slice))
        }
        return params

    def path(self, *args, **kwargs) -> str:
        return 'campaigns/rates'

    def parse_response(
        self,
        response: requests.Response,
        stream_slice: Mapping[str, Any] = None,
        *args,
        **kwargs
    ) -> Iterable[Mapping]:
        for record in Smi2MirtesenStream.parse_response(
            self,
            response=response,
            stream_slice=stream_slice,
            *args,
            **kwargs
        ):
            yield {
                **record,
                "campaign_id": stream_slice["parent"]["id"],
            }

    def stream_slices(self, *, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
        slices = list(super().stream_slices(sync_mode=sync_mode,
                                            cursor_field=cursor_field, stream_state=stream_state))
        yield from slices


class CampaignsNewsRates(Smi2MirtesenStream, ObjectRatesStream, HttpSubStream):
    primary_key = ["news_id", "date"]

    def __init__(
        self,
        authenticator: Union[AuthBase, HttpAuthenticator],
        client_name_constant: str,
        product_name_constant: str,
        custom_constants: Dict[str, Any],
        filters: List[Any],
        rates_granularity: RatesGranularity,
        date_from: datetime,
        date_to: datetime,
        campaigns_parent_stream: Campaigns,
        agency_id: Optional[int] = None,
    ):
        HttpSubStream.__init__(self, parent=campaigns_parent_stream)
        Smi2MirtesenStream.__init__(
            self,
            authenticator=authenticator,
            client_name_constant=client_name_constant,
            product_name_constant=product_name_constant,
            custom_constants=custom_constants,
            filters=filters,
            agency_id=agency_id,
        )
        ObjectRatesStream.__init__(
            self,
            date_from=date_from,
            date_to=date_to,
            rates_granularity=rates_granularity,
        )

    def build_condition(self, stream_slice: Mapping[str, Any] = None):
        if self.filters:
            return ['and', ["id", stream_slice["parent"]["id"]], self.filters]
        else:
            return ["id", stream_slice["parent"]["id"]]

    def request_params(self, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> MutableMapping[str, Any]:
        params = {
            **Smi2MirtesenStream.request_params(self, stream_slice=stream_slice, *args, **kwargs),
            **ObjectRatesStream.request_params(self, stream_slice=stream_slice, *args, **kwargs),
            "condition": json.dumps(self.build_condition(stream_slice=stream_slice))
        }
        return params

    def path(self, *args, **kwargs) -> str:
        return 'campaigns/rates'

    def parse_response(
        self,
        response: requests.Response,
        stream_slice: Mapping[str, Any] = None,
        *args,
        **kwargs
    ) -> Iterable[Mapping]:
        for record in Smi2MirtesenStream.parse_response(
            self,
            response=response,
            stream_slice=stream_slice,
            *args,
            **kwargs
        ):
            yield {
                **record,
                "campaign_id": stream_slice["parent"]["id"],
            }


class CampaignsRatesSum(CampaignsRates):
    def build_condition(self, stream_slice: Mapping[str, Any] = None):
        return self.filters

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from [{}]

    def parse_response(
        self,
        response: requests.Response,
        *args,
        **kwargs
    ) -> Iterable[Mapping]:
        yield from Smi2MirtesenStream.parse_response(
            self,
            response=response,
            *args,
            **kwargs
        )


class CampaignsNews(Smi2MirtesenStream, HttpSubStream):
    def __init__(
        self,
        authenticator: Union[AuthBase, HttpAuthenticator],
        campaigns_parent_stream: Campaigns,
        client_name_constant: str,
        product_name_constant: str,
        custom_constants: Dict[str, Any],
        filters: str,
        with_count: bool,
        with_rates: bool,
        rates_date_from: datetime,
        rates_date_to: datetime,
        agency_id: Optional[str] = None,
    ):

        HttpSubStream.__init__(self, parent=campaigns_parent_stream)
        Smi2MirtesenStream.__init__(
            self,
            authenticator=authenticator,
            client_name_constant=client_name_constant,
            product_name_constant=product_name_constant,
            custom_constants=custom_constants,
            filters=filters,
            agency_id=agency_id,
        )
        ObjectStream.__init__(
            self,
            rates_date_from=rates_date_from,
            rates_date_to=rates_date_to,
            with_count=with_count,
            with_rates=with_rates,
        )

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {
            **Smi2MirtesenStream.request_params(self, *args, **kwargs),
            **ObjectStream.request_params(self, *args, **kwargs),
        }

    def path(self, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> str:
        return f'campaigns/{stream_slice["parent"]["id"]}/news'


# Source
class SourceSmi2Mirtesen(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        config = self.transform_config(config)
        self.get_auth(config)
        try:
            json.loads(config.get("custom_constants_json", "{}"))
        except:
            raise Exception("Invalid custom_constants_json")
        try:
            json.loads(config.get("campaigns_filter_json", "[]"))
        except:
            raise Exception("Invalid campaigns_filter_json")
        try:
            json.loads(config.get("campaigns_news_filter_json", "[]"))
        except:
            raise Exception("Invalid campaigns_news_filter_json")

        return True, None

    def transform_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            rates_date_range_type = config["rates_date_range"]["rates_date_range_type"]
        except KeyError:
            config["rates_date_from"] = None
            config["rates_date_to"] = None
            return config
        if rates_date_range_type == "custom_date":
            config["rates_date_from"] = datetime.strptime(
                config["rates_date_range"].get("rates_date_from"), "%Y-%m-%d")
            config["rates_date_to"] = datetime.strptime(
                config["rates_date_range"].get("rates_date_to"), "%Y-%m-%d")
        elif rates_date_range_type == "last_n_days":
            config["rates_date_from"] = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
                days=config["rates_date_range"]["last_days_count"]
            )
            config["rates_date_to"] = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0)
        else:
            raise Exception(
                f"Invalid rates_date_range_type: {rates_date_range_type}")

        json_fields = [
            {"field_name": "campaigns_filter_json", "default_value": "[]"},
            {"field_name": "campaigns_news_filter_json", "default_value": "[]"},
            {"field_name": "campaigns_rates_filter_json", "default_value": "[]"},
            {"field_name": "campaigns_news_rates_filter_json", "default_value": "[]"},
            {"field_name": "custom_constants_json", "default_value": "{}"},
        ]

        for json_field in json_fields:
            if not config.get(json_field["field_name"], json_field["default_value"]):
                config[json_field["field_name"]] = json_field["default_value"]

        return config

    def get_auth(self, config) -> TokenAuthenticator:
        creds = config.get("credentials")
        if creds["auth_type"] == "username_password_auth":
            return UsernamePasswordOauth2Authenticator(username=creds["username"], password=creds["password"], client_id=creds["client_id"])
        else:
            raise Exception(f'Invalid auth type: {creds["auth_type"]}')

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.transform_config(config)
        authenticator = self.get_auth(config)

        constant_kwargs = dict(
            authenticator=authenticator,
            client_name_constant=config.get("client_name_constant"),
            product_name_constant=config.get("product_name_constant"),
            custom_constants=json.loads(
                config.get("custom_constants_json", "{}")),
            agency_id=config.get("agency_id"),

        )
        object_stream_kwargs = dict(
            rates_date_from=config["rates_date_from"],
            rates_date_to=config["rates_date_to"],
            with_count=config.get("with_count", True),
            with_rates=config.get("with_rates", True),
        )

        object_rates_kwargs = dict(
            date_from=config['rates_date_from'],
            date_to=config["rates_date_to"],
            rates_granularity=RatesGranularity(
                config.get('rates_time_granularity', 'day')
            ),
        )

        campaigns_stream_instance = Campaigns(
            filters=json.loads(
                config.get("campaigns_filter_json", "[]")),
            with_active_news_count=config.get(
                "campaigns_with_active_news_count", True),
            with_connected_site_clicks=config.get(
                "campaigns_with_connected_site_clicks", True),
            **constant_kwargs,
            **object_stream_kwargs,
        )
        return [
            campaigns_stream_instance,
            CampaignsNews(
                campaigns_parent_stream=campaigns_stream_instance,
                filters=json.loads(
                    config.get("campaigns_news_filter_json", "[]")
                ),
                **constant_kwargs,
                **object_stream_kwargs,
            ),
            CampaignsRates(
                **constant_kwargs,
                **object_rates_kwargs,
                filters=json.loads(
                    config.get("campaigns_rates_filter_json", "[]")
                ),
                campaigns_parent_stream=campaigns_stream_instance,
            ),
            CampaignsRatesSum(
                **constant_kwargs,
                **object_rates_kwargs,
                filters=json.loads(
                    config.get("campaigns_rates_filter_json", "[]")
                ),
                campaigns_parent_stream=campaigns_stream_instance,
            )
        ]

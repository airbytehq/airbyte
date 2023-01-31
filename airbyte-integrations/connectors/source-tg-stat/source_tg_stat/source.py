#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime
import json
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models import SyncMode
from datetime import datetime, timedelta


# Basic full refresh stream
class TgStatStream(HttpStream, ABC):
    url_base = "https://api.tgstat.ru/"

    def __init__(
        self,
        access_token: str,
        client_name_constant: Optional[str] = "",
        product_name_constant: Optional[str] = "",
        custom_constants: Optional[Mapping[str, Any]] = {},
    ):
        super().__init__(authenticator=None)
        self.access_token = access_token
        self.client_name_constant = client_name_constant
        self.product_name_constant = product_name_constant
        self.custom_constants = custom_constants

    def add_constants_to_record(self, record: Mapping[str, Any]):
        constants = {"__productName": self.product_name_constant, "__clientName": self.client_name_constant, **self.custom_constants}
        return {**record, **constants}

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {"token": self.access_token}

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        extra_properties = ["__productName", "__clientName", *self.custom_constants.keys()]
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}

        return schema

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class ChannelsListAsSlicesStream:
    def __init__(self, channels: List[str]):
        self.channels = channels

    def request_params(self, stream_slice: Mapping[str, any] = None, *args, **kwargs) -> MutableMapping[str, Any]:
        print("stream_slice", stream_slice)
        return {"channelId": stream_slice["channel_id"]}

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for channel_id in self.channels:
            print(f"yield channel_id {channel_id}")
            yield {"channel_id": channel_id}


class DateRangeStream:
    def __init__(self, date_from: datetime, date_to: datetime):
        self.date_from = date_from
        self.date_to = date_to

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {"startTime": int(self.date_from.timestamp()), "endTime": int(self.date_to.timestamp())}


class ChannelsList(ChannelsListAsSlicesStream, TgStatStream):
    primary_key = "id"

    def __init__(
        self,
        access_token: str,
        channels: list,
        client_name_constant: Optional[str] = "",
        product_name_constant: Optional[str] = "",
        custom_constants: Optional[Mapping[str, Any]] = {},
    ):
        TgStatStream.__init__(
            self,
            access_token=access_token,
            custom_constants=custom_constants,
            client_name_constant=client_name_constant,
            product_name_constant=product_name_constant,
        )
        ChannelsListAsSlicesStream.__init__(self, channels=channels)

    def path(self, *args, **kwargs) -> str:
        return "channels/get"

    def parse_response(self, response: requests.Response, *args, **kwargs) -> Iterable[Mapping]:
        yield self.add_constants_to_record(response.json()["response"])


class ChannelsDailyStatistics(ChannelsListAsSlicesStream, TgStatStream, DateRangeStream):
    primary_key = ["channel_id", "period"]

    def __init__(
        self,
        access_token: str,
        channels: list,
        date_from: datetime,
        date_to: datetime,
        custom_constants: Optional[Mapping[str, Any]] = {},
        client_name_constant: Optional[str] = "",
        product_name_constant: Optional[str] = "",
    ):
        TgStatStream.__init__(
            self,
            access_token=access_token,
            custom_constants=custom_constants,
            client_name_constant=client_name_constant,
            product_name_constant=product_name_constant,
        )
        ChannelsListAsSlicesStream.__init__(self, channels=channels)
        DateRangeStream.__init__(self, date_from=date_from, date_to=date_to)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return dict(
            **TgStatStream.request_params(self, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            **ChannelsListAsSlicesStream.request_params(
                self, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            ),
            **DateRangeStream.request_params(self, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            group="day",
        )

    def parse_response(
        self,
        response: requests.Response,
        stream_slice: Mapping[str, Any] = None,
        *args,
        **kwargs,
    ) -> Iterable[Mapping]:
        print(response.request.url)
        print(response.text)
        for record in response.json()["response"]:
            yield self.add_constants_to_record({**record, **stream_slice})


class ChannelsSubscribersDaily(ChannelsDailyStatistics):
    def path(self, *args, **kwargs) -> str:
        return "channels/subscribers"


class ChannelsViewsDaily(ChannelsDailyStatistics):
    def path(self, *args, **kwargs) -> str:
        return "channels/views"


class ChannelsAvgPostsReachDaily(ChannelsDailyStatistics):
    def path(self, *args, **kwargs) -> str:
        return "channels/avg-posts-reach"


class ChannelErrDaily(ChannelsDailyStatistics):
    def path(self, *args, **kwargs) -> str:
        return "channels/err"


class SourceTgStat(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        streams = self.streams(config)
        test_stream: ChannelsList = streams[0]
        print(next(test_stream.read_records(sync_mode=SyncMode.full_refresh)))

        return True, None

    def transform_config_date_range(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        date_range: Mapping[str, Any] = config.get("date_range", {})
        date_range_type: str = date_range.get("date_range_type")
        date_from: datetime = None
        date_to: datetime = None
        today_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        from_user_date_format = "%Y-%m-%d"

        if date_range_type == "custom_date":
            date_from = datetime.strptime(date_range.get("date_from"), from_user_date_format)
            date_to = datetime.strptime(date_range.get("date_to"), from_user_date_format)
        elif date_range_type == "from_start_date_to_today":
            date_from = datetime.strptime(date_range.get("date_from"), from_user_date_format)
            if date_range.get("should_load_today"):
                date_to = today_date
            else:
                date_to = today_date - timedelta(days=1)
        elif date_range_type == "last_n_days":
            date_from = today_date - timedelta(date_range.get("last_days_count"))
            if date_range.get("should_load_today"):
                date_to = today_date
            else:
                date_to = today_date - timedelta(days=1)

        config["date_from_transformed"], config["date_to_transformed"] = date_from, date_to
        return config

    def prepare_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        config = self.transform_config_date_range(config)
        config["custom_constants"] = json.loads(config.get("custom_constants_json", "{}"))
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        prepared_config = self.prepare_config(config)
        constants_kwargs = {
            "custom_constants": json.loads(prepared_config.get("custom_constants_json", "{}")),
            "client_name_constant": prepared_config["client_name_constant"],
            "product_name_constant": prepared_config["product_name_constant"],
        }
        channels_statistics_streams_kwargs = {
            "access_token": prepared_config["access_token"],
            "channels": prepared_config["channels"],
            "date_from": prepared_config["date_from_transformed"],
            "date_to": prepared_config["date_to_transformed"],
        }
        return [
            ChannelsList(access_token=prepared_config["access_token"], channels=prepared_config["channels"], **constants_kwargs),
            ChannelsSubscribersDaily(**channels_statistics_streams_kwargs, **constants_kwargs),
            ChannelErrDaily(**channels_statistics_streams_kwargs, **constants_kwargs),
            ChannelsAvgPostsReachDaily(**channels_statistics_streams_kwargs, **constants_kwargs),
            ChannelsViewsDaily(**channels_statistics_streams_kwargs, **constants_kwargs),
        ]

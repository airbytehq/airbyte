#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import logging
import time
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, UserDefinedBackoffException
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from requests.auth import AuthBase
from source_vk.auth import CredentialsCraftAuthenticator
from source_vk.utils import parse_url_query_params

logger = logging.getLogger("airbyte")


# Basic full refresh stream
class VkStream(HttpStream, ABC):
    VK_API_VERSION = "5.131"
    url_base = "https://api.vk.com/method/"
    transformer: TypeTransformer = TypeTransformer(
        config=TransformConfig.DefaultSchemaNormalization
    )
    pagination = False

    max_retries = 15

    def __init__(
        self, *, authenticator: HttpAuthenticator = None, date_from: datetime, date_to: datetime
    ):
        super().__init__(authenticator)
        self.date_from = date_from
        self.date_to = date_to

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def should_retry(self, response: requests.Response) -> bool:
        error_code = response.json().get("error", {}).get("error_code")
        return error_code in [1, 6, 9, 10, 29, 603]

    def should_skip_error(self, response: requests.Response) -> bool:
        error_code = response.json().get("error", {}).get("error_code")
        return error_code in [15, 801]

    def _send(
        self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]
    ) -> requests.Response:
        response = super()._send(request, request_kwargs)
        time.sleep(1 / 5)  # VK API has a limit of 5 requests per second
        if (
            response.json().get("error")
            and self.should_retry(response)
            and not self.should_skip_error(response)
        ):
            custom_backoff_time = self.backoff_time(response)
            error_message = self.error_message(response)
            if custom_backoff_time:
                raise UserDefinedBackoffException(
                    backoff=custom_backoff_time,
                    request=request,
                    response=response,
                    error_message=error_message,
                )
            else:
                raise DefaultBackoffException(
                    request=request, response=response, error_message=error_message
                )
        elif response.json().get("error") and not self.should_skip_error(response):
            raise Exception(self.error_message(response))
        return response

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}

    @property
    def max_time(self) -> Union[int, None]:
        """
        Override if needed. Specifies maximum total waiting time (in seconds) for backoff policy. Return None for no limit.
        """
        return None

    def error_message(self, response: requests.Response) -> str:
        error = response.json().get("error", {})
        if error:
            return f"Error: {error}, request params: {json.dumps(error.get('request_params'))}"
        else:
            return "Unexpected error. Couldn't parse error from response"

    def parse_response(
        self, response: requests.Response, stream_slice: Mapping[str, any] = None, **kwargs
    ) -> Iterable[Mapping]:
        if response.json().get("error") and self.should_skip_error(response):
            logger.warn(f"Skipping error: {self.error_message(response)}")
            yield from []
        else:
            for record in response.json()["response"]:
                yield {**record, "group_id": stream_slice["group_id"]}


class GroupStats(VkStream):
    primary_key = ["period_from", "period_to", "group_id"]

    def __init__(
        self,
        *,
        authenticator: HttpAuthenticator = None,
        date_from: datetime,
        date_to: datetime,
        group_ids: List[int] = None,
        chunks_config: Mapping[str, Any] = None,
    ):
        super().__init__(authenticator=authenticator, date_from=date_from, date_to=date_to)
        self.group_ids = group_ids
        self.should_split_into_chunks = chunks_config["chunk_mode_type"] == "split_into_chunks"
        self.chunk_size_in_days = chunks_config.get("chunk_size_in_days")

    def path(self, *args, **kwargs) -> str:
        return "stats.get"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "timestamp_from": int(stream_slice["date_from"].timestamp()),
            "timestamp_to": int(stream_slice["date_to"].timestamp()),
            "interval": "day",
            "group_id": stream_slice["group_id"],
            "v": self.VK_API_VERSION,
        }
        return params

    def stream_slices(self, *args, **kwargs) -> Iterable[Union[Mapping[str, Any], None]]:
        for group_id in self.group_ids:
            if self.should_split_into_chunks:
                day_chunks = list(self.day_chunks(self.date_from, self.date_to))
                for chunk in day_chunks:
                    yield {**chunk, "group_id": group_id}
            else:
                yield from [
                    {
                        "date_from": self.date_from,
                        "date_to": self.end_of_day(self.date_to),
                        "group_id": group_id,
                    }
                ]

    def day_chunks(self, date_from: datetime, date_to: datetime) -> Iterable[datetime]:
        cursor = date_from
        delta = timedelta(days=self.chunk_size_in_days - 1)
        while cursor < date_to:
            if cursor + delta > date_to:
                yield {"date_from": cursor, "date_to": self.end_of_day(date_to)}
                return
            yield {"date_from": cursor, "date_to": self.end_of_day(cursor + delta)}
            cursor = cursor + delta + timedelta(days=1)

    @staticmethod
    def end_of_day(date: datetime) -> datetime:
        return date.replace(hour=23, minute=59, second=59, microsecond=999999)


class ObjectStream(VkStream, ABC):
    page_size = 200

    def __init__(
        self,
        date_from: datetime,
        date_to: datetime,
        authenticator: HttpAuthenticator = None,
        group_ids: List[int] = None,
        chunks_config: Mapping[str, Any] = None,
    ):
        super().__init__(authenticator=authenticator, date_from=date_from, date_to=date_to)
        self.group_ids = group_ids
        self.should_split_into_chunks = chunks_config["chunk_mode_type"] == "split_into_chunks"

    def next_page_token(self, response: requests.Response) -> Mapping[str, Any]:
        latest_request_offset = parse_url_query_params(response.request.url).get("offset")

        if self.should_skip_error(response):
            return None

        if latest_request_offset:
            records_count = len(response.json()["response"]["items"])
            if records_count < self.page_size:
                return None
            return {"offset": int(latest_request_offset) + self.page_size}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["count"] = self.page_size

        if next_page_token:
            params["offset"] = next_page_token["offset"]
        else:
            params["offset"] = 0

        return params

    def stream_slices(
        self,
        *,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for group_id in self.group_ids:
            yield {"group_id": group_id}

    def parse_response(
        self, response: requests.Response, stream_slice: Mapping[str, any] = None, **kwargs
    ) -> Iterable[Mapping]:
        if response.json().get("error") and self.should_skip_error(response):
            logger.warn(f"Skipping error: {self.error_message(response)}")
            yield from []
        else:
            for record in response.json()["response"]["items"]:
                yield {**record, "group_id": stream_slice["group_id"]}


class GroupVideos(ObjectStream):
    primary_key = ["group_id", "id"]
    use_cache = True

    def path(self, *args, **kwargs) -> str:
        return "video.get"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {
            **super().request_params(stream_state, stream_slice, next_page_token),
            "owner_id": f"-{stream_slice['group_id']}",
            "v": self.VK_API_VERSION,
        }

    def parse_response(
        self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        for record in super().parse_response(response, stream_slice, **kwargs):
            for key in ["image", "first_frame", "title", "player"]:
                try:
                    record.pop(key)
                except KeyError:
                    pass
            yield record


class GroupPhotos(ObjectStream):
    use_cache = True

    primary_key = ["group_id", "id"]

    def path(self, *args, **kwargs) -> str:
        return "photos.get"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {
            **ObjectStream.request_params(self, stream_state, stream_slice, next_page_token),
            "owner_id": f"-{stream_slice['group_id']}",
            "v": self.VK_API_VERSION,
            "album_id": "wall",
            "extended": 1,
        }

    def parse_response(
        self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        for record in super().parse_response(response, stream_slice, **kwargs):
            try:
                record.pop("sizes")
            except KeyError:
                pass
            yield record


class GroupPhotosComments(ObjectStream, HttpSubStream):
    page_size = 100
    primary_key = ["group_id", "photo_id", "id"]

    def __init__(
        self,
        date_from: datetime,
        date_to: datetime,
        authenticator: HttpAuthenticator = None,
        group_ids: List[int] = None,
        chunks_config: Mapping[str, Any] = None,
        parent: GroupPhotos = None,
    ):
        ObjectStream.__init__(
            self,
            authenticator=authenticator,
            date_from=date_from,
            date_to=date_to,
            group_ids=group_ids,
            chunks_config=chunks_config,
        )
        self.parent = parent
        self._authenticator = authenticator

    def path(self, *args, **kwargs) -> str:
        return "photos.getComments"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {
            **ObjectStream.request_params(self, stream_state, stream_slice, next_page_token),
            "owner_id": f"-{stream_slice['group_id']}",
            "v": self.VK_API_VERSION,
            "photo_id": stream_slice["photo_id"],
            "fields": [
                "bdate",
                "common_count",
                "country",
                "domain",
                "nickname",
                "occupation",
                "screen_name",
            ],
        }

    def stream_slices(
        self,
        *,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for group_slice in ObjectStream.stream_slices(
            self, sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state
        ):
            for photo in HttpSubStream.stream_slices(
                self,
                sync_mode=sync_mode,
                cursor_field=cursor_field,
                stream_state=stream_state,
            ):
                record = photo["parent"]
                if record.get("comments", {}).get("count", 0) > 0:
                    yield {"photo_id": record["id"], "group_id": group_slice["group_id"]}

    def parse_response(
        self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        for record in super().parse_response(response, stream_slice, **kwargs):
            for key in ["text", "attachments"]:
                try:
                    record.pop(key)
                except KeyError:
                    pass
            yield {**record, **stream_slice}


class GroupVideosComments(ObjectStream, HttpSubStream):
    page_size = 100
    primary_key = ["group_id", "video_id", "id"]

    def __init__(
        self,
        date_from: datetime,
        date_to: datetime,
        authenticator: HttpAuthenticator = None,
        group_ids: List[int] = None,
        chunks_config: Mapping[str, Any] = None,
        parent: GroupVideos = None,
    ):
        ObjectStream.__init__(
            self,
            authenticator=authenticator,
            date_from=date_from,
            date_to=date_to,
            group_ids=group_ids,
            chunks_config=chunks_config,
        )
        self.parent = parent
        self._authenticator = authenticator

    def path(self, *args, **kwargs) -> str:
        return "video.getComments"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {
            **ObjectStream.request_params(self, stream_state, stream_slice, next_page_token),
            "owner_id": f"-{stream_slice['group_id']}",
            "v": self.VK_API_VERSION,
            "video_id": stream_slice["video_id"],
        }

    def stream_slices(
        self,
        *,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for group_slice in ObjectStream.stream_slices(
            self, sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state
        ):
            for video in HttpSubStream.stream_slices(
                self,
                sync_mode=sync_mode,
                cursor_field=cursor_field,
                stream_state=stream_state,
            ):
                record = video["parent"]
                if record.get("comments", 0) > 0:
                    yield {"video_id": record["id"], "group_id": group_slice["group_id"]}

    def parse_response(
        self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs
    ):
        for record in super().parse_response(response, stream_slice, **kwargs):
            for key in ["text", "attachments"]:
                try:
                    record.pop(key)
                except KeyError:
                    pass
            yield {**record, **stream_slice}


class GroupPosts(ObjectStream):
    page_size = 100
    primary_key = ["group_id", "id"]

    def path(self, *args, **kwargs) -> str:
        return "wall.get"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {
            **super().request_params(stream_state, stream_slice, next_page_token),
            "owner_id": f"-{stream_slice['group_id']}",
            "v": self.VK_API_VERSION,
        }

    def parse_response(
        self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        for record in super().parse_response(response, stream_slice, **kwargs):
            yield {**record, "group_id": stream_slice["group_id"]}


# Source
class SourceVk(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        config = self.transform_config_date_range(config)
        auth: Union[TokenAuthenticator, CredentialsCraftAuthenticator] = self.get_auth(config)

        if isinstance(auth, CredentialsCraftAuthenticator):
            success, message = auth.check_connection()
            if not success:
                return False, message

        access_denied_groups = []
        for group_id in config["group_ids"]:
            try:
                test_stream = GroupStats(
                    authenticator=auth,
                    date_from=config["date_from_transformed"],
                    date_to=config["date_to_transformed"],
                    group_ids=[group_id],
                )
                next(
                    test_stream.read_records(
                        sync_mode=SyncMode.full_refresh,
                        stream_slice={"group_id": group_id},
                    )
                )
            except Exception as e:
                if str(e).startswith("Error code"):
                    access_denied_groups.append(group_id)
        if access_denied_groups:
            return False, f"Access denied for groups: {access_denied_groups}"
        return True, None

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> TokenAuthenticator:
        auth_type = config["credentials"]["auth_type"]
        if auth_type == "access_token_auth":
            return TokenAuthenticator(token=config["credentials"]["access_token"])
        elif auth_type == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception(
                f"Invalid Auth type {auth_type}. Available: access_token_auth and credentials_craft_auth",
            )

    @staticmethod
    def transform_config_date_range(config: Mapping[str, Any]) -> Mapping[str, Any]:
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

    def get_date_range(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_auth(config)
        config = self.transform_config_date_range(config)
        chunks_config = config.get("chunks", {"chunk_mode_type": "dont_split"})
        shared_config = {
            "authenticator": auth,
            "date_from": config["date_from_transformed"],
            "date_to": config["date_to_transformed"],
        }
        return [
            GroupStats(**shared_config, group_ids=config["group_ids"], chunks_config=chunks_config),
            group_videos := GroupVideos(
                **shared_config, group_ids=config["group_ids"], chunks_config=chunks_config
            ),
            group_photos := GroupPhotos(
                **shared_config,
                group_ids=config["group_ids"],
                chunks_config=chunks_config,
            ),
            GroupPhotosComments(
                **shared_config,
                group_ids=config["group_ids"],
                chunks_config=chunks_config,
                parent=group_photos,
            ),
            GroupVideosComments(
                **shared_config,
                group_ids=config["group_ids"],
                chunks_config=chunks_config,
                parent=group_videos,
            ),
            GroupPosts(**shared_config, group_ids=config["group_ids"], chunks_config=chunks_config),
        ]

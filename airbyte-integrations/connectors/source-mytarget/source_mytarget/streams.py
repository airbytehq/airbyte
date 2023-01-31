from abc import ABC
from datetime import datetime, timedelta
from os import sync
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from unittest import skip

import requests
from airbyte_cdk.sources.streams.core import IncrementalMixin, SyncMode, package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

from .utils import DATE_FORMAT, chunks, date_minus_n_days, yesterday_minus_n_days
import json

# Basic full refresh stream
class MyTargetStream(HttpStream, ABC):
    transformer: TypeTransformer = TypeTransformer(config=TransformConfig.DefaultSchemaNormalization)

    url_base = "https://target.my.com/"
    primary_key = "id"
    page_size = 250

    def __init__(self, config: Mapping[str, Any], authenticator=None):
        super().__init__(authenticator)
        self.config = config

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        if not data.get("items"):
            return None

        return {"count": self.page_size, "offset": data["offset"] + self.page_size}

    def add_constants_to_record(self, record):
        constants = {
            "__productName": self.config["product_name"],
            "__clientName": self.config["client_name"],
        }
        constants.update(json.loads(self.config.get("custom_json", "{}")))
        record.update(constants)
        return record

    def get_json_schema(self):
        schema = super().get_json_schema()
        extra_properties = ["__productName", "__clientName"]
        custom_keys = json.loads(self.config.get("custom_json", "{}")).keys()
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}

        return schema

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        return {"limit": self.page_size, "offset": next_page_token["offset"] if next_page_token else 0}

    def parse_response(self, response: requests.Response, *args, **kwargs) -> Iterable[Mapping]:
        yield from map(self.add_constants_to_record, response.json()["items"])


class ObjectStream(MyTargetStream, ABC):
    object_name = None
    object_name_plural = None
    use_included_fields = True

    def __init__(self, config: Mapping[str, Any], authenticator: HttpAuthenticator = None, fields_to_include: Iterable[str] = []):
        super().__init__(authenticator=authenticator, config=config)
        self.fields_to_include = fields_to_include

    def path(self, *args, **kwargs) -> str:
        return f"api/v2/{self.object_name_plural}.json"

    def get_json_schema(self) -> Mapping[str, Any]:
        object_schema = super().get_json_schema()
        if self.fields_to_include:
            if not self.use_included_fields:
                raise Exception(f"Included fields is not supported for {self.name} stream.")
            included_fields_schemas = {}
            object_schema_properties_keys = object_schema["properties"].keys()
            for field_to_include_name in self.fields_to_include:
                if field_to_include_name not in object_schema_properties_keys:
                    raise KeyError(
                        f"Field '{field_to_include_name}' isn't available for {self.name} stream. "
                        f"Available fields: {object_schema_properties_keys}"
                    )
                included_fields_schemas[field_to_include_name] = object_schema["properties"][field_to_include_name]
            object_schema["properties"] = included_fields_schemas
            extra_properties = ["__productName", "__clientName"]
            custom_keys = json.loads(self.config.get("custom_json", "{}")).keys()
            extra_properties.extend(custom_keys)
            for key in extra_properties:
                object_schema["properties"][key] = {"type": ["null", "string"]}
        return object_schema

    @property
    def fields(self) -> Iterable[str]:
        excludes = ["__productName", "__clientName"]
        excludes += json.loads(self.config.get("custom_json", "{}")).keys()
        schema_keys = self.get_json_schema()["properties"].keys()
        return list(filter(lambda x: x not in excludes, schema_keys))

    @classmethod
    def included_fields_property_name(cls):
        return cls.object_name_plural + "_included_fields"

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token, **kwargs)
        params.update({"fields": ",".join(self.fields)})
        return params


class IncrementalStatisticsMixin(MyTargetStream, IncrementalMixin, HttpSubStream, ABC):
    """Docs: https://target.my.com/doc/api/ru/info/Statistics"""

    cursor_field = "date"
    parent_stream_class: MyTargetStream = None

    def __init__(self, authenticator: HttpAuthenticator, date_from: str, date_to: str, last_days: int, config: Mapping[str, Any]):
        MyTargetStream.__init__(self, config, authenticator)
        HttpSubStream.__init__(self, self.parent_stream_class(config, authenticator))
        self._authenticator = authenticator
        self.date_from = date_from
        self.date_to = date_to
        self.last_days = last_days
        self._cursor_value = None
        self.config = config

    def path(self, *args, **kwargs) -> str:
        return f"/api/v2/statistics/{self.parent.object_name_plural}/day.json"

    def request_params(self, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> MutableMapping[str, Any]:
        params = {"date_from": stream_slice["date_from"], "date_to": stream_slice["date_to"], "id": ",".join(stream_slice["ids"])}
        return params

    def next_page_token(self, *args) -> Optional[Mapping[str, Any]]:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("statistics")
        schema["properties"].update({self.object_id_property_name: {"type": ["null", "string"]}})
        extra_properties = ["__productName", "__clientName"]
        custom_keys = json.loads(self.config.get("custom_json", "{}")).keys()
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}

        return schema

    def parse_response(self, response: requests.Response, *args, **kwargs) -> Iterable[Mapping]:
        for obj in MyTargetStream.parse_response(self, response, *args, **kwargs):
            obj_id = obj.get("id")
            if not obj_id:
                self.logger.warning("Caught obj with obj_id None, obj: ", str(obj))

            for day_record in obj.get("rows", []):
                day_record.update({self.object_id_property_name: obj_id})
                yield self.add_constants_to_record(day_record)

    @property
    def primary_key(self):
        return [self.object_id_property_name, "date"]

    @property
    def object_id_property_name(self):
        return self.parent.object_name + "_id"

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: self.date_from}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def read_records(
        self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Mapping[str, Any]]:
        for record in MyTargetStream.read_records(self, sync_mode, cursor_field, stream_slice, stream_state):
            # Update cursor value only when all obj IDs chunks processed.
            if stream_slice["should_update_state_after"]:
                latest_record_date = record[self.cursor_field]
                self._cursor_value = max(self._cursor_value, latest_record_date) if self._cursor_value else latest_record_date
            yield record

    @staticmethod
    def date_chunks_ranges(date_from: str, skip_first: bool, date_to: str = None) -> List[str]:
        """
        Returns a list of each day between the date_from and yesterday.
        The return value is a list of dicts {'date': date_string}.
        """
        print("skip_first", skip_first)
        date_from = datetime.strptime(date_from, DATE_FORMAT)
        if date_to:
            date_to = datetime.strptime(date_to, DATE_FORMAT)
        else:
            date_to = datetime.now() - timedelta(1)

        if skip_first:
            date_from += timedelta(days=1)
        dates_by_day = []
        while date_from <= date_to:
            dates_by_day.append(date_from.strftime(DATE_FORMAT))
            date_from += timedelta(days=1)
        dates_chunks = list(chunks(dates_by_day, 30))
        chunks_ranges = []
        for chunk in dates_chunks:
            if chunk:
                chunks_ranges.append({"date_from": min(chunk), "date_to": max(chunk)})
        print("chunks_ranges", chunks_ranges)
        return chunks_ranges

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        stream_state always describing already loaded records state, and also we shouldn't load
        today date because of it's incomplition, so in this case stream_state always will be yesterday date.
        We don't need to load already loaded data, so we skip stream_state to next day, instead of
        user inputted date_from - in this case we should replicate first day too, because we don't have
        first day data on first incremental sync or in FullRefresh mode.
        """
        print("stream_state", bool(stream_state))
        date_from = None
        if sync_mode == SyncMode.full_refresh:
            if self.last_days:
                # ignore self.date_from, always use last_days
                date_from = yesterday_minus_n_days(self.last_days)
            else:
                date_from = self.date_from
        if sync_mode == SyncMode.incremental:
            # if not first load (stream_state has been properly passed to stream):
            if stream_state and self.cursor_field in stream_state:
                # if state is abnormal (state date is more than yesterday), we force it to yesterday
                if datetime.strtime(stream_state[self.cursor_field], DATE_FORMAT).date() > datetime.today().date() - timedelta(1):
                    stream_state[self.cursor_field] = (datetime.today().date() - timedelta(1)).strftime(DATE_FORMAT)

                # force last_days based loading if it is passed, otherwise use stream_state
                if self.last_days:
                    date_from = date_minus_n_days(stream_state[self.cursor_field])
                    # set stream_state to None so as not to break the logic of skip_first since
                    #   this parameter is based on stream_state existanse.
                    # when we use last_days, we always bypass stream_state logic
                    #   and force connector to just stupid load last days data on every sync
                    stream_state = None
                else:
                    date_from = stream_state[self.cursor_field]
            # if first load:
            else:
                if self.last_days:
                    date_from = yesterday_minus_n_days(self.last_days)
                else:
                    date_from = self.date_from
        date_ranges = self.date_chunks_ranges(date_from, skip_first=bool(stream_state), date_to=self.date_to)
        if not date_ranges:
            # Skip for unnecessary objects IDs retrieving - there will be no any slices if we have no dates to load
            self.logger.info(f"{self.name} stream doesn\t need refreshing.")
            return []

        # chunked because of 200 object ids per request restriction
        objects_ids_chunks = list(
            chunks([str(r["parent"]["id"]) for r in list(HttpSubStream.stream_slices(self, sync_mode, cursor_field, stream_state))], 200)
        )
        slices = []
        for date_range in date_ranges:
            for ids_chunk_num, objects_ids_chunk in enumerate(objects_ids_chunks, start=1):
                slices.append(
                    {
                        "ids": objects_ids_chunk,
                        "date_from": date_range["date_from"],
                        "date_to": date_range["date_to"],
                        "should_update_state_after": ids_chunk_num == len(objects_ids_chunks),
                    }
                )
        return slices


class Campaigns(ObjectStream):
    """https://target.my.com/doc/api/ru/resource/Campaigns"""

    use_cache = True
    object_name = "campaign"
    object_name_plural = "campaigns"


class Banners(ObjectStream):
    """https://target.my.com/doc/api/ru/resource/Banners"""

    use_cache = True
    object_name = "banner"
    object_name_plural = "banners"


class PadsTrees(ObjectStream):
    """https://target.my.com/doc/api/ru/resource/PadsTree"""

    object_name = "pads_tree"
    object_name_plural = "pads_trees"
    use_included_fields = False

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, *args, **kwargs) -> Optional[Mapping[str, Any]]:
        return None


class PackagesPads(ObjectStream):
    """https://target.my.com/doc/api/ru/resource/PackagesPads"""

    object_name = "package_pad"
    object_name_plural = "packages_pads"
    use_included_fields = False

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, *args, **kwargs) -> Optional[Mapping[str, Any]]:
        return None


class CampaignsStatistics(IncrementalStatisticsMixin):
    parent_stream_class = Campaigns


class BannersStatistics(IncrementalStatisticsMixin):
    parent_stream_class = Banners

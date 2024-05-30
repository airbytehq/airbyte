#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union

import elasticsearch.exceptions
import requests
from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStreamStatus,
    ConfiguredAirbyteStream,
    AirbyteStateType
)
from airbyte_cdk.models import (
    ConfiguredAirbyteCatalog,
    FailureType,
    StreamDescriptor,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources import AbstractSource
from source_elastic_search_v2.connector_state_manager import ElasticConnectorStateManager
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.sources.streams.http.http import HttpStream
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.schema_helpers import split_config
from airbyte_cdk.utils.event_timing import create_timer
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from elasticsearch import Elasticsearch

StreamData = Union[Mapping[str, Any], AirbyteMessage]

# Streams that only support full refresh don't have a suitable cursor so this sentinel
# value is used to indicate that stream should not load the incoming state value
FULL_REFRESH_SENTINEL_STATE_KEY = "__ab_full_refresh_state_message"

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


# Basic full refresh stream
class ElasticSearchV2Stream(HttpStream, ABC):
    url_base = "http://aes-statistic01.prod.dld:9200"
    client: Elasticsearch = Elasticsearch(url_base)
    date_start = ""
    pit = None
    primary_key = "_id"

    def __init__(self, date_start):
        super().__init__()
        self.date_start = date_start

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/_search"

    @property
    def http_method(self) -> str:
        """
        Override if needed. See get_request_data/get_request_json if using POST/PUT/PATCH.
        """
        return "POST"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        docs = response.json()["hits"]["hits"]
        pit_id = response.json()["pit_id"]
        if response.status_code == 200 and docs != []:
            search_after = docs[len(docs) - 1].get("sort")
            return {"search_after": search_after, "pit_id": pit_id}
        else:
            # Case when no more pages
            try:
                self.client.close_point_in_time(id=self.pit.body["id"])
            except elasticsearch.exceptions.NotFoundError as e:
                logging.info("Not PIT found")
            return None

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        return {"content-type": "application/json"}

    def request_body_data(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: int = 0,
    ) -> Optional[Union[Mapping, str]]:
        """
        Override when creating POST/PUT/PATCH requests to populate the body of the request with a non-JSON payload.

        If returns a ready text that it will be sent as is.
        If returns a dict that it will be converted to a urlencoded form.
        E.g. {"key1": "value1", "key2": "value2"} => "key1=value1&key2=value2"

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """

        if self.state == {'updated_at': {}}:
            date_filter_start = self.date_start
        else:
            date_filter_start = self.state.get("updated_at")

        # If this is a new sync
        if next_page_token is None:
            self.pit = self.client.open_point_in_time(index=self.index, keep_alive="10m")
            payload = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "updated_at": {
                                        "gte": date_filter_start
                                    }
                                }
                            }
                        ]
                    }
                },
                "pit": {
                    "id": self.pit.body["id"],
                    "keep_alive": "10m"
                },
                "size": 10000,
                "sort": [
                    {"updated_at": {"order": "asc", "format": "strict_date_optional_time_nanos", "numeric_type": "date_nanos"}}
                ]
            }

        # If this is the next page of a sync
        else:
            pit_id = next_page_token["pit_id"]
            search_after = next_page_token["search_after"]

            payload = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "updated_at": {
                                        "gte": date_filter_start
                                    }
                                }
                            }
                        ]
                    }
                },
                "pit": {
                    "id": pit_id,
                    "keep_alive": "10m"
                },
                "size": 10000,
                "search_after": search_after,
                "sort": [
                    {"updated_at": {"order": "asc", "format": "strict_date_optional_time_nanos", "numeric_type": "date_nanos"}}
                ]
            }

        return json.dumps(payload)


# Basic incremental stream
class IncrementalElasticSearchV2Stream(ElasticSearchV2Stream, IncrementalMixin, ABC):
    # point in time
    pit = ""
    date_start = ""
    cursor_value = {}
    cursor_field = "updated_at"

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return "updated_at"

    @property
    def state(self) -> MutableMapping[str, Any]:
        """State getter, should return state in form that can serialized to a string and send to the output
        as a STATE AirbyteMessage.

        A good example of a state is a _cursor_value:
            {
                self.cursor_field: "_cursor_value"
            }

         State should try to be as small as possible but at the same time descriptive enough to restore
         syncing process from the point where it stopped.
        """

        return {self.cursor_field: self.cursor_value}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """State setter, accept state serialized by state getter."""
        try:
            timestamp_dt = datetime.fromisoformat(value[self.cursor_field])
            new_timestamp_dt = timestamp_dt - timedelta(hours=7)
            new_timestamp_str = new_timestamp_dt.isoformat()
            self.cursor_value = new_timestamp_str
        except KeyError:
            self.cursor_value = value["updated_at"]
        except TypeError:
            pass

    def get_updated_state(self, a, b):
        return {self.cursor_field: self.cursor_value}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        hits = response.json()["hits"]["hits"]

        try:
            last_document_timestamp = hits[len(hits) - 1].get("_source")
            self.state = last_document_timestamp
        except KeyError as k:
            last_document_timestamp = hits[len(hits) - 1].get("_source")
            self.state = last_document_timestamp
        except IndexError as e:
            print("No more documents")

        for hit in hits:
            data = hit["_source"]
            data["_id"] = hit["_id"]
            yield data


# Source
class SourceElasticSearchV2(AbstractSource):
    namespace = ""
    state = {}

    # can be overridden to change an input state.
    @classmethod
    def read_state(cls, state_path: str) -> Union[List[AirbyteStateMessage], MutableMapping[str, Any]]:
        """
        Retrieves the input state of a sync by reading from the specified JSON file. Incoming state can be deserialized into either
        a JSON object for legacy state input or as a list of AirbyteStateMessages for the per-stream state format. Regardless of the
        incoming input type, it will always be transformed and output as a list of AirbyteStateMessage(s).
        :param state_path: The filepath to where the stream states are located
        :return: The complete stream state based on the connector's previous sync
        """
        try:
            state_obj = BaseConnector._read_json_file(state_path)
        except FileNotFoundError:
            state_obj = [
                {'type': 'STREAM', 'stream': {'stream_state': {}, 'stream_descriptor': {'name': 'SourceElasticSearchV2', 'namespace': ''}}}]
        except TypeError:
            state_obj = [
                {'type': 'STREAM', 'stream': {'stream_state': {}, 'stream_descriptor': {'name': 'SourceElasticSearchV2', 'namespace': ''}}}]
        print("state_obj : " + str(state_obj))
        try:
            state = state_obj[0].get("stream").get("stream_state")
        except KeyError:
            state = {}
        print("state : " + str(state))
        return state

    def read(
            self,
            logger: logging.Logger,
            config: Mapping[str, Any],
            catalog: ConfiguredAirbyteCatalog,
            state: Optional[Union[List[AirbyteStateMessage], MutableMapping[str, Any]]] = None,
    ) -> Iterator[AirbyteMessage]:
        """Implements the Read operation from the Airbyte Specification. See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/."""
        logger.info(f"Starting syncing {self.name}")
        config, internal_config = split_config(config)
        # TODO assert all streams exist in the connector
        # get the streams once in case the connector needs to make any queries to generate them
        stream_instances = {s.name: s for s in self.streams(config)}
        state_manager = ElasticConnectorStateManager(stream_instance_map={s.stream.name: s.stream for s in catalog.streams}, state=state)
        self._stream_to_instance_map = stream_instances

        stream_name_to_exception: MutableMapping[str, AirbyteTracedException] = {}

        with create_timer(self.name) as timer:
            for configured_stream in catalog.streams:
                stream_instance = stream_instances.get(configured_stream.stream.name)
                stream_instance.state = state.get(stream_instance.name)
                if not stream_instance:
                    if not self.raise_exception_on_missing_stream:
                        continue
                    raise KeyError(
                        f"The stream {configured_stream.stream.name} no longer exists in the configuration. "
                        f"Refresh the schema in replication settings and remove this stream from future sync attempts."
                    )

                try:
                    timer.start_event(f"Syncing stream {configured_stream.stream.name}")
                    stream_is_available, reason = stream_instance.check_availability(logger, self)
                    if not stream_is_available:
                        logger.warning(f"Skipped syncing stream '{stream_instance.name}' because it was unavailable. {reason}")
                        continue
                    logger.info(f"Marking stream {configured_stream.stream.name} as STARTED")
                    yield stream_status_as_airbyte_message(configured_stream.stream, AirbyteStreamStatus.STARTED)
                    yield from self._read_stream(
                        logger=logger,
                        stream_instance=stream_instance,
                        configured_stream=configured_stream,
                        state_manager=state_manager,
                        internal_config=internal_config,
                    )
                    logger.info(f"Marking stream {configured_stream.stream.name} as STOPPED")
                    yield stream_status_as_airbyte_message(configured_stream.stream, AirbyteStreamStatus.COMPLETE)
                except AirbyteTracedException as e:
                    logger.exception(f"Encountered an exception while reading stream {configured_stream.stream.name}")
                    logger.info(f"Marking stream {configured_stream.stream.name} as STOPPED")
                    yield stream_status_as_airbyte_message(configured_stream.stream, AirbyteStreamStatus.INCOMPLETE)
                    yield e.as_sanitized_airbyte_message(stream_descriptor=StreamDescriptor(name=configured_stream.stream.name))
                    stream_name_to_exception[stream_instance.name] = e
                    if self.stop_sync_on_stream_failure:
                        logger.info(
                            f"Stopping sync on error from stream {configured_stream.stream.name} because {self.name} does not support continuing syncs on error."
                        )
                        break
                except Exception as e:
                    yield from self._emit_queued_messages()
                    logger.exception(f"Encountered an exception while reading stream {configured_stream.stream.name}")
                    logger.info(f"Marking stream {configured_stream.stream.name} as STOPPED")
                    yield stream_status_as_airbyte_message(configured_stream.stream, AirbyteStreamStatus.INCOMPLETE)
                    display_message = stream_instance.get_error_display_message(e)
                    if display_message:
                        traced_exception = AirbyteTracedException.from_exception(e, message=display_message)
                    else:
                        traced_exception = AirbyteTracedException.from_exception(e)
                    yield traced_exception.as_sanitized_airbyte_message(
                        stream_descriptor=StreamDescriptor(name=configured_stream.stream.name)
                    )
                    stream_name_to_exception[stream_instance.name] = traced_exception
                    if self.stop_sync_on_stream_failure:
                        logger.info(f"{self.name} does not support continuing syncs on error from stream {configured_stream.stream.name}")
                        break
                finally:
                    timer.finish_event()
                    logger.info(f"Finished syncing {configured_stream.stream.name}")
                    logger.info(timer.report())

        if len(stream_name_to_exception) > 0:
            error_message = self._generate_failed_streams_error_message(stream_name_to_exception)
            logger.info(error_message)
            # We still raise at least one exception when a stream raises an exception because the platform currently relies
            # on a non-zero exit code to determine if a sync attempt has failed. We also raise the exception as a config_error
            # type because this combined error isn't actionable, but rather the previously emitted individual errors.
            raise AirbyteTracedException(message=error_message, failure_type=FailureType.config_error)
        logger.info(f"Finished syncing {self.name}")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        client = Elasticsearch("http://aes-statistic01.prod.dld:9200")
        response = client.ping(request_timeout=5)

        return response, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        date_start = config["date_start"]

        return [Campaigns(date_start), Accounts(date_start), Creatives(date_start)]

    def _read_stream(
            self,
            logger: logging.Logger,
            stream_instance: Stream,
            configured_stream: ConfiguredAirbyteStream,
            state_manager: ElasticConnectorStateManager,
            internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        if internal_config.page_size and isinstance(stream_instance, HttpStream):
            logger.info(f"Setting page size for {stream_instance.name} to {internal_config.page_size}")
            stream_instance.page_size = internal_config.page_size
        logger.info(
            f"Syncing configured stream: {configured_stream.stream.name}",
            extra={
                "sync_mode": configured_stream.sync_mode,
                "primary_key": configured_stream.primary_key,
                "cursor_field": configured_stream.cursor_field,
            },
        )
        stream_instance.log_stream_sync_configuration()

        stream_name = configured_stream.stream.name
        # The platform always passes stream state regardless of sync mode. We shouldn't need to consider this case within the
        # connector, but right now we need to prevent accidental usage of the previous stream state
        # self.state[stream_instance.name] = stream_instance.state
        # logger.info(f"Setting state of {self.name} stream to {self.state}")

        record_iterator = stream_instance.read(
            configured_stream,
            logger,
            self._slice_logger,
            self.state,
            state_manager,
            internal_config,
        )

        record_counter = 0
        logger.info(f"Syncing stream: {stream_name} ")
        for record_data_or_message in record_iterator:
            record = self._get_message(record_data_or_message, stream_instance)
            if record.type == MessageType.RECORD:
                record_counter += 1
                if record_counter == 1:
                    logger.info(f"Marking stream {stream_name} as RUNNING")
                    # If we just read the first record of the stream, emit the transition to the RUNNING state
                    yield stream_status_as_airbyte_message(configured_stream.stream, AirbyteStreamStatus.RUNNING)
            yield from self._emit_queued_messages()
            yield record

        logger.info(f"Read {record_counter} records from {stream_name} stream")
        logger.info(f"Setting state of {self.name} stream to {self.state}")
        self.state[stream_instance.name] = stream_instance.state
        airbyte_state_message = self._checkpoint_state(self.state, state_manager)
        yield airbyte_state_message

    def _checkpoint_state(  # type: ignore  # ignoring typing for ConnectorStateManager because of circular dependencies
            self,
            stream_state: Mapping[str, Any],
            state_manager,
    ) -> AirbyteMessage:
        # First attempt to retrieve the current state using the stream's state property. We receive an AttributeError if the state
        # property is not implemented by the stream instance and as a fallback, use the stream_state retrieved from the stream
        # instance's deprecated get_updated_state() method.
        state_manager.update_state_for_stream(
            self.name, self.namespace, self.state  # type: ignore # we know the field might not exist...
        )

        return state_manager.create_state_message(self.name, self.namespace)


class Creatives(IncrementalElasticSearchV2Stream):
    index = "statistics_ad_creative*"


class Campaigns(IncrementalElasticSearchV2Stream):
    index = "statistics_campaign*"


class Accounts(IncrementalElasticSearchV2Stream):
    index = "statistics_account*"

#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, List, Mapping, Optional, Union

import freezegun
import isodate
import pendulum
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
)
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.sources.types import Record, StreamSlice
from sources.streams.core import StreamData

_CONFIG = {
    "start_date": "2024-07-01T00:00:00.000Z"
}

_CATALOG = ConfiguredAirbyteCatalog(
    streams=[
        ConfiguredAirbyteStream(
            stream=AirbyteStream(name="party_members", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            sync_mode=SyncMode.incremental,
            destination_sync_mode=DestinationSyncMode.append,
        ),
        ConfiguredAirbyteStream(
            stream=AirbyteStream(name="palaces", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.append,
        ),
        ConfiguredAirbyteStream(
            stream=AirbyteStream(name="locations", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            sync_mode=SyncMode.incremental,
            destination_sync_mode=DestinationSyncMode.append,
        ),
        ConfiguredAirbyteStream(
            stream=AirbyteStream(name="party_members_skills", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.append,
        )
    ]
)

_MANIFEST = {
  "version": "5.0.0",
  "definitions": {
    "selector": {
      "type": "RecordSelector",
      "extractor": {
        "type": "DpathExtractor",
        "field_path": ["{{ parameters.get('data_field') }}"]
      }
    },
    "requester": {
      "type": "HttpRequester",
      "url_base": "https://persona.metaverse.com",
      "http_method": "GET",
      "authenticator": {
        "type": "BasicHttpAuthenticator",
        "username": "{{ config['api_key'] }}",
        "password": "{{ config['secret_key'] }}"
      },
      "error_handler": {
        "type": "DefaultErrorHandler",
        "response_filters": [
          {
            "http_codes": [403],
            "action": "FAIL",
            "failure_type": "config_error",
            "error_message": "Access denied due to lack of permission or invalid API/Secret key or wrong data region."
          },
          {
            "http_codes": [404],
            "action": "IGNORE",
            "error_message": "No data available for the time range requested."
          }
        ]
      }
    },
    "retriever": {
      "type": "SimpleRetriever",
      "record_selector": {
        "$ref": "#/definitions/selector"
      },
      "paginator": {
        "type": "NoPagination"
      },
      "requester": {
        "$ref": "#/definitions/requester"
      }
    },
    "incremental_cursor": {
      "type": "DatetimeBasedCursor",
      "start_datetime": {
        "datetime": "{{ format_datetime(config['start_date'], '%Y-%m-%d') }}"
      },
      "end_datetime": {
        "datetime": "{{ now_utc().strftime('%Y-%m-%d') }}"
      },
      "datetime_format": "%Y-%m-%d",
      "cursor_datetime_formats": ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"],
      "cursor_granularity": "P1D",
      "step": "P15D",
      "cursor_field": "updated_at",
      "lookback_window": "P5D",
      "start_time_option": {
        "type": "RequestOption",
        "field_name": "start",
        "inject_into": "request_parameter"
      },
      "end_time_option": {
        "type": "RequestOption",
        "field_name": "end",
        "inject_into": "request_parameter"
      }
    },
    "base_stream": {
      "retriever": {
        "$ref": "#/definitions/retriever"
      }
    },
    "base_incremental_stream": {
      "retriever": {
        "$ref": "#/definitions/retriever",
        "requester": {
          "$ref": "#/definitions/requester"
        }
      },
      "incremental_sync": {
        "$ref": "#/definitions/incremental_cursor"
      }
    },
    "party_members_stream": {
      "$ref": "#/definitions/base_incremental_stream",
      "retriever": {
        "$ref": "#/definitions/base_incremental_stream/retriever",
        "record_selector": {
          "type": "RecordSelector",
          "extractor": {
            "type": "DpathExtractor",
            "field_path": []
          }
        }
      },
      "$parameters": {
        "name": "party_members",
        "primary_key": "id",
        "path": "/party_members"
      },
      "schema_loader": {
        "type": "InlineSchemaLoader",
        "schema": {
          "$schema": "https://json-schema.org/draft-07/schema#",
          "type": "object",
          "properties": {
            "id": {
              "description": "The identifier",
              "type": ["null", "string"],
            },
            "name": {
              "description": "The name of the party member",
              "type": ["null", "string"]
            }
          }
        }
      }
    },
    "palaces_stream": {
      "$ref": "#/definitions/base_stream",
      "$parameters": {
        "name": "palaces",
        "primary_key": "id",
        "path": "/party_members"
      },
      "schema_loader": {
        "type": "InlineSchemaLoader",
        "schema": {
          "$schema": "https://json-schema.org/draft-07/schema#",
          "type": "object",
          "properties": {
            "id": {
              "description": "The identifier",
              "type": ["null", "string"],
            },
            "name": {
              "description": "The name of the metaverse palace",
              "type": ["null", "string"]
            }
          }
        }
      }
    },
    "locations_stream": {
      "$ref": "#/definitions/base_incremental_stream",
      "retriever": {
        "$ref": "#/definitions/base_incremental_stream/retriever",
        "requester": {
          "$ref": "#/definitions/base_incremental_stream/retriever/requester",
          "request_parameters": {
            "m": "active",
            "i": "1",
            "g": "country"
          }
        },
        "record_selector": {
          "type": "RecordSelector",
          "extractor": {
            "type": "DpathExtractor",
            "field_path": []
          }
        }
      },
      "incremental_sync": {
        "$ref": "#/definitions/incremental_cursor",
        "step": "P1M",
        "cursor_field": "updated_at"
      },
      "$parameters": {
        "name": "locations",
        "primary_key": "id",
        "path": "/locations"
      },
      "schema_loader": {
        "type": "InlineSchemaLoader",
        "schema": {
          "$schema": "https://json-schema.org/draft-07/schema#",
          "type": "object",
          "properties": {
            "id": {
              "description": "The identifier",
              "type": ["null", "string"],
            },
            "name": {
              "description": "The name of the neighborhood location",
              "type": ["null", "string"]
            }
          }
        }
      }
    },
    "party_members_skills_stream": {
      "$ref": "#/definitions/base_stream",
      "retriever": {
        "$ref": "#/definitions/base_incremental_stream/retriever",
        "record_selector": {
          "type": "RecordSelector",
          "extractor": {
            "type": "DpathExtractor",
            "field_path": []
          }
        },
        "partition_router": {
          "type": "SubstreamPartitionRouter",
          "parent_stream_configs": [
            {
              "type": "ParentStreamConfig",
              "stream": "#/definitions/party_members_stream",
              "parent_key": "id",
              "partition_field": "party_member_id",
            }
          ]
        }
      },
      "$parameters": {
        "name": "party_members_skills",
        "primary_key": "id",
        "path": "/party_members_skills"
      },
      "schema_loader": {
        "type": "InlineSchemaLoader",
        "schema": {
          "$schema": "https://json-schema.org/draft-07/schema#",
          "type": "object",
          "properties": {
            "id": {
              "description": "The identifier",
              "type": ["null", "string"],
            },
            "name": {
              "description": "The name of the party member",
              "type": ["null", "string"]
            }
          }
        }
      }
    },
  },
  "streams": [
    "#/definitions/party_members_stream",
    "#/definitions/palaces_stream",
    "#/definitions/locations_stream",
    "#/definitions/party_members_skills_stream"
  ],
  "check": {
    "stream_names": ["party_members", "palaces", "locations"]
  }
}


class DeclarativeStreamDecorator(Stream):
    """
    Helper class that wraps an existing DeclarativeStream but allows for overriding the output of read_records() to
    make it easier to mock behavior and test how low-code streams integrate with the Concurrent CDK.
    """

    def __init__(self, declarative_stream: DeclarativeStream, slice_to_records_mapping: Mapping[tuple[str, str], List[Mapping[str, Any]]]):
        self._declarative_stream = declarative_stream
        self._slice_to_records_mapping = slice_to_records_mapping

    @property
    def name(self) -> str:
        return self._declarative_stream.name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._declarative_stream.primary_key

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if isinstance(stream_slice, StreamSlice):
            slice_key = (stream_slice.get("start_time"), stream_slice.get("end_time"))
            if slice_key in self._slice_to_records_mapping:
                yield from self._slice_to_records_mapping.get(slice_key)
            else:
                yield from []
        else:
            raise ValueError(f"stream_slice should be of type StreamSlice, but received {type(stream_slice)}")

    def get_json_schema(self) -> Mapping[str, Any]:
        return self._declarative_stream.get_json_schema()


def test_separate_streams():
    """
    Tests the separating of low-code streams into ones that can be processed concurrently vs ones that must be processed concurrently
    """

    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="party_members", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="palaces", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="locations", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="party_members_skills", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )

    state = []

    source = ConcurrentDeclarativeSource(source_config=_MANIFEST, config=_CONFIG, catalog=catalog, state=state)
    concurrent_streams = source._concurrent_streams
    synchronous_streams = source._synchronous_streams

    # 2 incremental streams
    assert len(concurrent_streams) == 2
    concurrent_stream_0, concurrent_stream_1 = concurrent_streams
    assert isinstance(concurrent_stream_0, DefaultStream)
    assert concurrent_stream_0.name == "party_members"
    assert isinstance(concurrent_stream_1, DefaultStream)
    assert concurrent_stream_1.name == "locations"

    # 1 full refresh stream, 1 substream
    assert len(synchronous_streams) == 2
    synchronous_stream_0, synchronous_stream_1 = synchronous_streams
    assert isinstance(synchronous_stream_0, DeclarativeStream)
    assert synchronous_stream_0.name == "palaces"
    assert isinstance(synchronous_stream_1, DeclarativeStream)
    assert synchronous_stream_1.name == "party_members_skills"


@freezegun.freeze_time(time_to_freeze=datetime(2024, 9, 1, 0, 0, 0, 0, tzinfo=timezone.utc))
def test_create_concurrent_cursor():
    """
    Validate that the ConcurrentDeclarativeSource properly instantiates a ConcurrentCursor from the
    low-code DatetimeBasedCursor component
    """

    incoming_locations_state = {
        "slices": [
            {"start": "2024-07-01T00:00:00.000Z", "end": "2024-07-31T00:00:00.000Z"},
        ],
        "state_type": "date-range"
    }

    state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="locations", namespace=None),
                stream_state=AirbyteStateBlob(**incoming_locations_state)
            ),
        ),
    ]

    source = ConcurrentDeclarativeSource(source_config=_MANIFEST, config=_CONFIG, catalog=_CATALOG, state=state)

    party_members_stream = source._concurrent_streams[0]
    assert isinstance(party_members_stream, DefaultStream)
    party_members_cursor = party_members_stream.cursor

    assert isinstance(party_members_cursor, ConcurrentCursor)
    assert party_members_cursor._stream_name == "party_members"
    assert party_members_cursor._cursor_field.cursor_field_key == "updated_at"
    assert party_members_cursor._start == pendulum.parse(_CONFIG.get("start_date"))
    assert party_members_cursor._end_provider() == datetime(year=2024, month=9, day=1, tzinfo=timezone.utc)
    assert party_members_cursor._slice_boundary_fields == ("start_time", "end_time")
    assert party_members_cursor._slice_range == timedelta(days=15)
    assert party_members_cursor._lookback_window == timedelta(days=5)
    assert party_members_cursor._cursor_granularity == timedelta(days=1)

    locations_stream = source._concurrent_streams[1]
    assert isinstance(locations_stream, DefaultStream)
    locations_cursor = locations_stream.cursor

    assert isinstance(locations_cursor, ConcurrentCursor)
    assert locations_cursor._stream_name == "locations"
    assert locations_cursor._cursor_field.cursor_field_key == "updated_at"
    assert locations_cursor._start == pendulum.parse(_CONFIG.get("start_date"))
    assert locations_cursor._end_provider() == datetime(year=2024, month=9, day=1, tzinfo=timezone.utc)
    assert locations_cursor._slice_boundary_fields == ("start_time", "end_time")
    assert locations_cursor._slice_range == isodate.Duration(months=1)
    assert locations_cursor._lookback_window == timedelta(days=5)
    assert locations_cursor._cursor_granularity == timedelta(days=1)
    assert locations_cursor.state == {
        "slices": [
            {
                "start": datetime(2024, 7, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
                "end": datetime(2024, 7, 31, 0, 0, 0, 0, tzinfo=timezone.utc),
            }
        ],
        "state_type": "date-range"
    }


def test_check():
    """
    Verifies that the ConcurrentDeclarativeSource check command is run against concurrent and synchronous streams
    """
    source = ConcurrentDeclarativeSource(source_config=_MANIFEST, config=_CONFIG, catalog=None, state=None)

    actual_connection_state = source.check(logger=source.logger, config=_CONFIG)

    assert actual_connection_state


def test_discover():
    """
    Verifies that the ConcurrentDeclarativeSource discover command returns concurrent and synchronous catalog definitions
    """
    expected_stream_names = ["party_members", "palaces", "locations", "party_members_skills"]

    source = ConcurrentDeclarativeSource(source_config=_MANIFEST, config=_CONFIG, catalog=None, state=None)

    actual_catalog = source.discover(logger=source.logger, config=_CONFIG)

    assert len(actual_catalog.streams) == 4
    assert actual_catalog.streams[0].name in expected_stream_names
    assert actual_catalog.streams[1].name in expected_stream_names
    assert actual_catalog.streams[2].name in expected_stream_names
    assert actual_catalog.streams[3].name in expected_stream_names


@freezegun.freeze_time("2024-09-10T00:00:00")
def test_read_with_concurrent_and_synchronous_streams():
    """
    Verifies that a ConcurrentDeclarativeSource processes concurrent streams followed by synchronous streams
    """

    source = ConcurrentDeclarativeSource(source_config=_MANIFEST, config=_CONFIG, catalog=_CATALOG, state=None)

    for i, _ in enumerate(source._concurrent_streams):
        stream = source._concurrent_streams[i]._stream_partition_generator._stream
        if isinstance(stream, DeclarativeStream):
            decorated_stream = create_wrapped_stream(stream=stream)
            source._concurrent_streams[i]._stream_partition_generator._stream = decorated_stream
        else:
            raise ValueError(f"Expecting stream as type DeclarativeStream, but got {type(stream)}")

    for i, _ in enumerate(source._synchronous_streams):
        stream = source._synchronous_streams[i]
        if isinstance(stream, DeclarativeStream):
            decorated_stream = create_wrapped_stream(stream=stream)
            source._synchronous_streams[i] = decorated_stream
        else:
            raise ValueError(f"Expecting stream as type DeclarativeStream, but got {type(stream)}")

    messages = list(source.read(logger=source.logger, config=_CONFIG, catalog=_CATALOG, state=[]))

    # Expects 15 records, 5 slices, 3 records each slice
    party_members_records = get_records_for_stream("party_members", messages)
    assert len(party_members_records) == 15

    party_members_states = get_states_for_stream(stream_name="party_members", messages=messages)
    assert len(party_members_states) == 6
    assert party_members_states[5].stream.stream_state == AirbyteStateBlob(
        state_type="date-range",
        slices=[{"start": "2024-07-01", "end": "2024-09-09"}]
    )

    # Expects 12 records, 3 slices, 4 records each slice
    locations_records = get_records_for_stream(stream_name="locations", messages=messages)
    assert len(locations_records) == 12

    # 3 partitions == 3 state messages + final state message
    # Because we cannot guarantee the order partitions finish, we only validate that the final state has the latest checkpoint value
    locations_states = get_states_for_stream(stream_name="locations", messages=messages)
    assert len(locations_states) == 4
    assert locations_states[3].stream.stream_state == AirbyteStateBlob(
        state_type="date-range",
        slices=[{"start": "2024-07-01", "end": "2024-09-09"}]
    )

    # Expects 7 records, 1 empty slice, 7 records in slice
    palaces_records = get_records_for_stream("palaces", messages)
    assert len(palaces_records) == 7

    palaces_states = get_states_for_stream(stream_name="palaces", messages=messages)
    assert len(palaces_states) == 1
    assert palaces_states[0].stream.stream_state == AirbyteStateBlob(__ab_no_cursor_state_message=True)

    # Expects 3 records, 1 empty slice, 3 records in slice
    party_members_skills_records = get_records_for_stream("party_members_skills", messages)
    assert len(party_members_skills_records) == 3

    party_members_skills_states = get_states_for_stream(stream_name="party_members_skills", messages=messages)
    assert len(party_members_skills_states) == 1
    assert party_members_skills_states[0].stream.stream_state == AirbyteStateBlob(__ab_no_cursor_state_message=True)


@freezegun.freeze_time("2024-09-10T00:00:00")
def test_read_with_concurrent_and_synchronous_streams_with_concurrent_state():
    """
    Verifies that a ConcurrentDeclarativeSource processes concurrent streams correctly using the incoming
    concurrent state format
    """

    state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="locations", namespace=None),
                stream_state=AirbyteStateBlob(
                    state_type="date-range",
                    slices=[{"start": "2024-07-01", "end": "2024-07-31"}],
                ),
            ),
        ),
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="party_members", namespace=None),
                stream_state=AirbyteStateBlob(
                    state_type="date-range",
                    slices=[
                        {"start": "2024-07-16", "end": "2024-07-30"},
                        {"start": "2024-08-15", "end": "2024-08-29"},
                        {"start": "2024-08-30", "end": "2024-09-09"},
                    ]
                ),
            ),
        ),
    ]

    source = ConcurrentDeclarativeSource(source_config=_MANIFEST, config=_CONFIG, catalog=_CATALOG, state=state)

    for i, _ in enumerate(source._concurrent_streams):
        stream = source._concurrent_streams[i]._stream_partition_generator._stream
        if isinstance(stream, DeclarativeStream):
            decorated_stream = create_wrapped_stream(stream=stream)
            source._concurrent_streams[i]._stream_partition_generator._stream = decorated_stream
        else:
            raise ValueError(f"Expecting stream as type DeclarativeStream, but got {type(stream)}")

    for i, _ in enumerate(source._synchronous_streams):
        stream = source._synchronous_streams[i]
        if isinstance(stream, DeclarativeStream):
            decorated_stream = create_wrapped_stream(stream=stream)
            source._synchronous_streams[i] = decorated_stream
        else:
            raise ValueError(f"Expecting stream as type DeclarativeStream, but got {type(stream)}")

    messages = list(source.read(logger=source.logger, config=_CONFIG, catalog=_CATALOG, state=state))

    # Expects 8 records, skip successful intervals and are left with 2 slices, 4 records each slice
    locations_records = get_records_for_stream("locations", messages)
    assert len(locations_records) == 8

    locations_states = get_states_for_stream(stream_name="locations", messages=messages)
    assert len(locations_states) == 3
    assert locations_states[2].stream.stream_state == AirbyteStateBlob(
        state_type="date-range",
        slices=[{"start": "2024-07-01", "end": "2024-09-09"}]
    )

    # Expects 12 records, skip successful intervals and are left with 4 slices, 3 records each slice
    party_members_records = get_records_for_stream("party_members", messages)
    assert len(party_members_records) == 12

    party_members_states = get_states_for_stream(stream_name="party_members", messages=messages)
    assert len(party_members_states) == 5
    assert party_members_states[4].stream.stream_state == AirbyteStateBlob(
        state_type="date-range",
        slices=[{"start": "2024-07-01", "end": "2024-09-09"}]  # weird, why'd this end up as 2024-09-10 is it because of cursor granularity?
    )

    # Expects 7 records, 1 empty slice, 7 records in slice
    palaces_records = get_records_for_stream("palaces", messages)
    assert len(palaces_records) == 7

    # Expects 3 records, 1 empty slice, 3 records in slice
    party_members_skills_records = get_records_for_stream("party_members_skills", messages)
    assert len(party_members_skills_records) == 3


@freezegun.freeze_time("2024-09-10T00:00:00")
def test_read_with_concurrent_and_synchronous_streams_with_sequential_state():
    """
    Verifies that a ConcurrentDeclarativeSource processes concurrent streams correctly using the incoming
    legacy state format
    """
    state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="locations", namespace=None),
                stream_state=AirbyteStateBlob(updated_at="2024-08-06"),
            ),
        ),
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="party_members", namespace=None),
                stream_state=AirbyteStateBlob(updated_at="2024-08-20"),
            ),
        )
    ]

    source = ConcurrentDeclarativeSource(source_config=_MANIFEST, config=_CONFIG, catalog=_CATALOG, state=state)

    for i, _ in enumerate(source._concurrent_streams):
        stream = source._concurrent_streams[i]._stream_partition_generator._stream
        if isinstance(stream, DeclarativeStream):
            decorated_stream = create_wrapped_stream(stream=stream)
            source._concurrent_streams[i]._stream_partition_generator._stream = decorated_stream
        else:
            raise ValueError(f"Expecting stream as type DeclarativeStream, but got {type(stream)}")

    for i, _ in enumerate(source._synchronous_streams):
        stream = source._synchronous_streams[i]
        if isinstance(stream, DeclarativeStream):
            decorated_stream = create_wrapped_stream(stream=stream)
            source._synchronous_streams[i] = decorated_stream
        else:
            raise ValueError(f"Expecting stream as type DeclarativeStream, but got {type(stream)}")

    messages = list(source.read(logger=source.logger, config=_CONFIG, catalog=_CATALOG, state=state))

    # Expects 8 records, skip successful intervals and are left with 2 slices, 4 records each slice
    locations_records = get_records_for_stream("locations", messages)
    assert len(locations_records) == 8

    # Expects 6 records, skip successful intervals and are left with 2 slices, 4 records each slice
    party_members_records = get_records_for_stream("party_members", messages)
    assert len(party_members_records) == 6

    # Expects 7 records, 1 empty slice, 7 records in slice
    palaces_records = get_records_for_stream("palaces", messages)
    assert len(palaces_records) == 7

    # Expects 3 records, 1 empty slice, 3 records in slice
    party_members_skills_records = get_records_for_stream("party_members_skills", messages)
    assert len(party_members_skills_records) == 3


@freezegun.freeze_time("2024-09-10T00:00:00")
def test_read_concurrent_with_failing_partition_in_the_middle():
    """
    Verify that partial state is emitted when only some partitions are successful during a concurrent sync attempt
    """



@freezegun.freeze_time("2024-09-10T00:00:00")
def test_read_concurrent_skip_streams_not_in_catalog():
    """
    Verifies that the ConcurrentDeclarativeSource only syncs streams that are specified in the incoming ConfiguredCatalog
    """

    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="palaces", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="locations", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
            ),
        ]
    )

    source = ConcurrentDeclarativeSource(source_config=_MANIFEST, config=_CONFIG, catalog=catalog, state=None)

    for i, _ in enumerate(source._concurrent_streams):
        stream = source._concurrent_streams[i]._stream_partition_generator._stream
        if isinstance(stream, DeclarativeStream):
            decorated_stream = create_wrapped_stream(stream=stream)
            source._concurrent_streams[i]._stream_partition_generator._stream = decorated_stream
        else:
            raise ValueError(f"Expecting stream as type DeclarativeStream, but got {type(stream)}")

    for i, _ in enumerate(source._synchronous_streams):
        stream = source._synchronous_streams[i]
        if isinstance(stream, DeclarativeStream):
            decorated_stream = create_wrapped_stream(stream=stream)
            source._synchronous_streams[i] = decorated_stream
        else:
            raise ValueError(f"Expecting stream as type DeclarativeStream, but got {type(stream)}")

    messages = list(source.read(logger=source.logger, config=_CONFIG, catalog=catalog, state=[]))

    locations_records = get_records_for_stream(stream_name="locations", messages=messages)
    assert len(locations_records) == 12
    locations_states = get_states_for_stream(stream_name="locations", messages=messages)
    assert len(locations_states) == 4

    palaces_records = get_records_for_stream("palaces", messages)
    assert len(palaces_records) == 7
    palaces_states = get_states_for_stream(stream_name="palaces", messages=messages)
    assert len(palaces_states) == 1

    assert len(get_records_for_stream(stream_name="party_members", messages=messages)) == 0
    assert len(get_states_for_stream(stream_name="party_members", messages=messages)) == 0

    assert len(get_records_for_stream(stream_name="party_members_skills", messages=messages)) == 0
    assert len(get_states_for_stream(stream_name="party_members_skills", messages=messages)) == 0


def test_read_concurrent_streams_only():
    pass


def test_read_synchronous_streams_only():
    pass


def create_wrapped_stream(stream: DeclarativeStream) -> Stream:
    slice_to_records_mapping = get_mocked_read_records_output(stream_name=stream.name)

    return DeclarativeStreamDecorator(declarative_stream=stream, slice_to_records_mapping=slice_to_records_mapping)


def get_mocked_read_records_output(stream_name: str) -> Mapping[tuple[str, str], List[StreamData]]:
    match stream_name:
        case "locations":
            slices = [
                # Slices used during first incremental sync
                StreamSlice(cursor_slice={"start": "2024-07-01", "end": "2024-07-31"}, partition={}),
                StreamSlice(cursor_slice={"start": "2024-08-01", "end": "2024-08-31"}, partition={}),
                StreamSlice(cursor_slice={"start": "2024-09-01", "end": "2024-09-09"}, partition={}),

                # Slices used during incremental checkpoint sync
                StreamSlice(cursor_slice={'start': '2024-07-26', 'end': '2024-08-25'}, partition={}),
                StreamSlice(cursor_slice={'start': '2024-08-26', 'end': '2024-09-09'}, partition={}),
            ]

            records = [
                {"id": "444", "name": "Yongen-jaya"},
                {"id": "scramble", "name": "Shibuya"},
                {"id": "aoyama", "name": "Aoyama-itchome"},
                {"id": "shin123", "name": "Shinjuku"},
            ]
        case "party_members":
            slices = [
                # Slices used during first incremental sync
                StreamSlice(cursor_slice={"start": "2024-07-01", "end": "2024-07-15"}, partition={}),
                StreamSlice(cursor_slice={"start": "2024-07-16", "end": "2024-07-30"}, partition={}),
                StreamSlice(cursor_slice={"start": "2024-07-31", "end": "2024-08-14"}, partition={}),
                StreamSlice(cursor_slice={"start": "2024-08-15", "end": "2024-08-29"}, partition={}),
                StreamSlice(cursor_slice={"start": "2024-08-30", "end": "2024-09-09"}, partition={}),

                # Slices used during incremental checkpoint sync. Unsuccessful partitions use the P5D lookback window which explains
                # the skew of records midway through
                StreamSlice(cursor_slice={"start": "2024-07-01", "end": "2024-07-16"}, partition={}),
                StreamSlice(cursor_slice={'start': '2024-07-30', 'end': '2024-08-13'}, partition={}),
                StreamSlice(cursor_slice={'start': '2024-08-14', 'end': '2024-08-14'}, partition={}),
                StreamSlice(cursor_slice={'start': '2024-09-04', 'end': '2024-09-10'}, partition={}),
            ]

            records = [
                {"id": "amamiya", "first_name": "ren", "last_name": "amamiya"},
                {"id": "nijima", "first_name": "makoto", "last_name": "nijima"},
                {"id": "yoshizawa", "first_name": "sumire", "last_name": "yoshizawa"},
            ]
        case "palaces":
            slices = [StreamSlice(cursor_slice={}, partition={})]

            records = [
                {"id": "0", "world": "castle", "owner": "kamoshida"},
                {"id": "1", "world": "museum", "owner": "madarame"},
                {"id": "2", "world": "bank", "owner": "kaneshiro"},
                {"id": "3", "world": "pyramid", "owner": "futaba"},
                {"id": "4", "world": "spaceport", "owner": "okumura"},
                {"id": "5", "world": "casino", "owner": "nijima"},
                {"id": "6", "world": "cruiser", "owner": "shido"},
            ]
        case "party_members_skills":
            slices = [StreamSlice(cursor_slice={}, partition={})]

            records = [
                {"id": "0", "name": "hassou tobi"},
                {"id": "1", "name": "mafreidyne"},
                {"id": "2", "name": "myriad truths"},
            ]
        case _:
            raise ValueError(f"Stream '{stream_name}' does not have associated mocked records")

    return {(_slice.get("start"), _slice.get("end")): [Record(data=stream_data, associated_slice=_slice) for stream_data in records] for _slice in slices}


def get_records_for_stream(stream_name: str, messages: List[AirbyteMessage]) -> List[AirbyteRecordMessage]:
    return [message.record for message in messages if message.record and message.record.stream == stream_name]


def get_states_for_stream(stream_name: str, messages: List[AirbyteMessage]) -> List[AirbyteStateMessage]:
    return [message.state for message in messages if message.state and message.state.stream.stream_descriptor.name == stream_name]

#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta, datetime, timezone

import freezegun
import isodate
import pendulum
from airbyte_cdk.models import AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor, AirbyteStateBlob, Type

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode

from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream

_CONFIG = {
    "start_date": "2024-07-01T00:00:00.000Z"
}

_CATALOG = ConfiguredAirbyteCatalog(
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


def test_separate_streams_concurrent_only():
    """
    Test generation of a catalog that only contains concurrent streams. TBD if this is needed
    """
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="party_members", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="locations", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )


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

    source = ConcurrentDeclarativeSource(source_config=_MANIFEST, config=_CONFIG, catalog=catalog, state=state)

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


def test_read():
    """
    Verifies that a ConcurrentDeclarativeSource processes concurrent streams followed by synchronous streams
    """
    source = ConcurrentDeclarativeSource(source_config=_MANIFEST, config=_CONFIG, catalog=None, state=None)

    state = []

    # we need to find a way to mock at the very edge of concurrent probably the underlying DeclarativeStream.read_records()
    # aka the thing that gets invoked by the partition generator and return 5 records.
    # and if we can simulate 2-3 partitions on the concurrent flow that should equate to 15 records
    # and maybe we need to assert or count the invocations or on the Default stream count something to verify that it went through
    # that flow. might be tricky...

    messages = list(source.read(logger=source.logger, config=_CONFIG, catalog=_CATALOG, state=state))

    assert len(messages) == 1

def test_read_concurrent_streams_only():
    pass


def test_read_synchronous_streams_only():
    pass

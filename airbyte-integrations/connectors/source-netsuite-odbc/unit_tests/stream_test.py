import pytest
from source_netsuite_odbc.streams import NetsuiteODBCStream, NETSUITE_PAGINATION_INTERVAL
from airbyte_cdk.models import AirbyteStream, SyncMode
from datetime import date


@pytest.fixture
def stream():
    expected_json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "accountnumber": {"type": ["string", "null"]},
            "acquisitionsource": {"type": ["integer", "null"]},
            "alcoholrecipienttype": {"type": ["string", "null"]},
            "altemail": {"type": ["string", "null"]},
            "altname": {"type": ["string", "null"]},
            "altphone": {"type": ["string", "null"]},
            "assignedwebsite": {"type": ["integer", "null"]},
            "lastmodifieddate": {"type": ["string", "null"], "format": "date-time"},
        },
    }
    return AirbyteStream(
        name="Customer",
        json_schema=expected_json_schema,
        supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        source_defined_cursor=True,
        default_cursor_field=["lastmodifieddate"],
        source_defined_primary_key=None,
        namespace=None,
        primary_key=["id"],
    )


@pytest.fixture
def stream_state():
    return {
        "last_date_updated": "2023-01-01",
        "last_values_seen": {"id": 200},
    }


def test_get_range_to_fetch(stream_state, stream):
    stream = NetsuiteODBCStream({}, "test", stream, config={"starting_year": 2020})
    today = date.today()
    year = today.year

    range = stream.get_range_to_fetch(SyncMode.full_refresh, stream_state)
    assert range == (date(2020, 1, 1), date(year + 1, 12, 1))
    range = stream.get_range_to_fetch(SyncMode.incremental, stream_state)
    assert range == (date(2023, 1, 1), date(year + 1, 12, 1))


def test_stream_slices(stream_state, stream):
    netsuite_stream = NetsuiteODBCStream({}, "test", stream, config={"starting_year": 2020})
    slices = netsuite_stream.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)
    assert slices[0] == {"first_day": date(2023, 1, 1), "last_day": date(2023, 12, 31)}
    assert slices[1] == {"first_day": date(2024, 1, 1), "last_day": date(2024, 12, 31)}
    today = date.today()
    year = today.year
    assert len(slices) == year - 2023 + 3  # all years from 2023 to current year, + next year, +1 null state


def test_get_updated_state(stream_state, stream):
    netsuite_stream = NetsuiteODBCStream({}, "test", stream, config={"starting_year": 2020})
    netsuite_stream.incremental_most_recent_value_seen = "2022-01-01"
    netsuite_stream.primary_key_last_value_seen = {"id": 155}
    new_state = netsuite_stream.get_updated_state(stream_state, {})
    assert new_state == {"last_date_updated": "2023-01-01", "last_values_seen": {"id": 200}}


def test_generate_ordered_query(stream_state, stream):
    netsuite_stream = NetsuiteODBCStream({}, "test", stream, config={"starting_year": 2020})
    query = netsuite_stream.generate_query({"first_day": date(2024, 1, 1), "last_day": date(2024, 12, 31)})
    stripped_query = query.replace(" ", "").replace("\n", "")
    expected_query = f"""SELECT TOP {NETSUITE_PAGINATION_INTERVAL} accountnumber, acquisitionsource, alcoholrecipienttype, altemail, altname, altphone, assignedwebsite, lastmodifieddate FROM testWHERE ((id > -10000)) AND lastmodifieddate >= to_timestamp('2024-01-01', 'YYYY-MM-DD') AND lastmodifieddate <= to_timestamp('2024-12-31', 'YYYY-MM-DD')ORDER BY id ASC,lastmodifieddateASC""".replace(
        " ", ""
    )

    assert stripped_query == expected_query


def test_processing_new_state(stream_state, stream):
    netsuite_stream = NetsuiteODBCStream({}, "test", stream, config={"starting_year": 2020})
    netsuite_stream.process_input_stream_state(stream_state)
    assert netsuite_stream.primary_key_last_value_seen == {"id": 200}
    assert netsuite_stream.incremental_most_recent_value_seen == "2023-01-01"

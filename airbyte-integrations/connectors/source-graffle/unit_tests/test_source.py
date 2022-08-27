from source_graffle.source import SourceGraffle


def test_streams():
    config = {
        "company_id": "test_company_id",
        "start_datetime": "test_start_datetime"
    }
    source = SourceGraffle()
    streams = source.streams(config)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number

from source_google_ads.source import chunk_date_range, AdGroupAdReport


def test_chunk_date_range():
    start_date = "2021-03-04"
    end_date = "2021-05-04"
    conversion_window = 14
    field = "date"
    response = chunk_date_range(start_date, end_date, conversion_window, field)
    assert [{'date': '2021-02-18'}, {'date': '2021-03-18'},
            {'date': '2021-04-18'}] == response


# this requires the config because instantiating a stream creates a google client. TODO refactor so client can be mocked.
def test_get_updated_state(config):
    client = AdGroupAdReport(config)
    current_state_stream = {}
    latest_record = {"segments.date": "2020-01-01"}

    new_stream_state = client.get_updated_state(
        current_state_stream, latest_record)
    assert new_stream_state == {'segments.date': '2020-01-01'}

    current_state_stream = {'segments.date': '2020-01-01'}
    latest_record = {"segments.date": "2020-02-01"}
    new_stream_state = client.get_updated_state(
        current_state_stream, latest_record)
    assert new_stream_state == {'segments.date': '2020-02-01'}

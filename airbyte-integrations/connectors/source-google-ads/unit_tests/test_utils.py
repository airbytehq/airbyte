from source_google_ads.utils import Utils


def test_get_date_params():
    stream_slice = {"date": "2020-01-01"}
    cursor_field = "date"

    response = Utils.get_date_params(stream_slice, cursor_field)
    assert response == ('2020-01-02', '2020-02-01')

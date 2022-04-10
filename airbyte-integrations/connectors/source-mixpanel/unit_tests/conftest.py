import pendulum
import pytest


@pytest.fixture
def config():
    return {
        "api_secret": "7607999ef26581e81726777b7b79f20e70e75602",
        "attribution_window": 5,
        "project_timezone": "UTC",
        "select_properties_by_default": True,
        "start_date": pendulum.parse("2017-01-25T00:00:00Z").date(),
        "end_date": pendulum.parse("2017-02-25T00:00:00Z").date(),
        "region": "US"
    }

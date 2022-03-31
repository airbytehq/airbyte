import pendulum
import pytest


@pytest.fixture(name="config")
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


@pytest.fixture(name="funnels_response")
def funnels_response():
    return setup_response(200, {
        "meta": {
            "dates": [
                "2016-09-12"
                "2016-09-19"
                "2016-09-26"
            ]
        },
        "data": {
            "2016-09-12": {
                "steps": [],
                "analysis": {
                    "completion": 20524,
                    "starting_amount": 32688,
                    "steps": 2,
                    "worst": 1,
                }
            },
            "2016-09-19": {
                "steps": [],
                "analysis": {
                    "completion": 20500,
                    "starting_amount": 34750,
                    "steps": 2,
                    "worst": 1,
                }
            }
        }
    })


@pytest.fixture(name="funnels_list_response")
def funnels_list_response():
    return setup_response(200, [
        {
            "funnel_id": 1,
            "name": "Signup funnel"
        }
    ])


@pytest.fixture(name="engage_schema_response")
def engage_schema_response():
    return setup_response(200, {
        "results": {
            "$browser": {
                "count": 124,
                "type": "string"
            },
            "$browser_version": {
                "count": 124,
                "type": "string"
            },
            "$created": {
                "count": 124,
                "type": "string"
            }
        }
    })


@pytest.fixture(name="annotations_response")
def annotations_response():
    return setup_response(200, {
        "annotations": [
            {
                "id": 640999,
                "project_id": 2117889,
                "date": "2021-06-16 00:00:00",
                "description": "Looks good"
            },
            {
                "id": 640000,
                "project_id": 2117889,
                "date": "2021-06-16 00:00:00",
                "description": "Looks bad"
            }
        ]
    })


@pytest.fixture(name="revenue_response")
def revenue_response():
    return setup_response(200, {
        'computed_at': '2021-07-03T12:43:48.889421+00:00',
        'results': {
            '$overall': {
                'amount': 0.0,
                'count': 124,
                'paid_count': 0
            },
            '2021-06-01': {
                'amount': 0.0,
                'count': 124,
                'paid_count': 0
            },
            '2021-06-02': {
                'amount': 0.0,
                'count': 124,
                'paid_count': 0
            }
        },
        'session_id': '162...',
        'status': 'ok'
    })


@pytest.fixture(name="export_schema_response")
def export_schema_response():
    return setup_response(200, {
        "$browser": {
            "count": 6
        },
        "$browser_version": {
            "count": 6
        },
        "$current_url": {
            "count": 6
        },
        "mp_lib": {
            "count": 6
        },
        "noninteraction": {
            "count": 6
        },
        "$event_name": {
            "count": 6
        },
        "$duration_s": {},
        "$event_count": {},
        "$origin_end": {},
        "$origin_start": {}
    })


@pytest.fixture(name="export_response")
def export_response():
    return setup_response(200, {
        "event": "Viewed E-commerce Page",
        "properties": {
            "time": 1623860880,
            "distinct_id": "1d694fd9-31a5-4b99-9eef-ae63112063ed",
            "$browser": "Chrome",
            "$browser_version": "91.0.4472.101",
            "$current_url": "https://unblockdata.com/solutions/e-commerce/",
            "$insert_id": "c5eed127-c747-59c8-a5ed-d766f48e39a4",
            "$mp_api_endpoint": "api.mixpanel.com",
            "mp_lib": "Segment: analytics-wordpress",
            "mp_processing_time_ms": 1623886083321,
            "noninteraction": True
        }
    })


@pytest.fixture(name="empty_response_ok")
def empty_response_ok():
    return setup_response(200, {})


@pytest.fixture(name="empty_response_bad")
def empty_response_bad():
    return setup_response(400, {})


def setup_response(status, body):
    return [
        {
            "json": body,
            "status_code": status
        }
    ]

#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy

from pytest import fixture


@fixture(name="config")
def config_fixture(requests_mock):
    return {
        "site_urls": ["https://example.com/"],
        "start_date": "2022-01-01",
        "end_date": "2022-02-01",
        "authorization": {
            "auth_type": "Client",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "refresh_token": "refresh_token",
        },
        "custom_reports": '[{"name": "custom_dimensions", "dimensions": ["date", "country", "device"]}]',
        "custom_reports_array": [{"name": "custom_dimensions", "dimensions": ["date", "country", "device"]}],
    }


@fixture(name="service_account_config")
def config_service_account_fixture(requests_mock):
    return {
        "site_urls": ["https://example.com/"],
        "start_date": "2022-01-01",
        "end_date": "2022-02-01",
        "authorization": {
            "auth_type": "Service",
            "service_account_info": '{\n  "type": "service_account",\n  "project_id": "test",\n  "private_key_id": "123",\n  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BBQEFAASCBKcwggSjAgEAAoIBAQDCJPUvep0vXeWb\\nqiwnDxWdd8D75FWJBaYB3rjZvBBhZiY3sA7DmEOj+NJHl4PiPzP8tDZl9MyLBWEc\\neTFSmHSBYSqxax9AOLzWXfLzUezjediIRsGC/Eq9Ue0rkDdMcdcfzQ5J9RDDI1DF\\n1UBxVHFOf7DOSOU7meNPFjAO68aITErvnTh/XL1wWC28PYL351hs57WwLSQTuW0e\\ncUw9XUOE977+qJ4Cs3ZM5c10eid5DDWS4heFG/9hEkobXy34BNdeDodfe9xGSJxD\\nFoAhADj6jMn1z7YgsUG7zpsyW8yh2LtnYdT+fMqIl0FeB4dt0kB3uU1f6vqgo97p\\ndibK6DQ3AgMBAAECggEADWZPz+eZreyNDbnokzrDMw7SMIof1AKIsZKMPDPAE1Pu\\ndlbkWS0LGhs92p6DOUKqFWdHMkrh/tEvuy94L1G1CAr+gqe4mY4KjPPuC7I1wRuM\\n50ovWtlliGL9SIDxkbw+IB4SJIBrS3SgCg+AA6WgezQ5lHtLUXPh6ivHXfhGLlKR\\nI+Gow93UklbxcT57ezeDZVn0U3iUG1H7NkE0livyTTGEMm6GxUqxje7axA4ZVfRL\\nRVrNAHQTihPTThmN/p47Wbh6C8m7o1/cutYDk52CuCjuifxNINlak1ZimSEJ7mcY\\nSIglnTmndQImwiyeDbITtJ3gyYiJerjHnMAYH+VInQKBgQD5HH1tKBxZouozdweu\\n6lpTyko+TBa/3Eo2pgFxbJrKe3pBhkNWVLrCukZxWDFkKSbC+5xaSNGnh/lP/6FX\\nWHWBuBL8R5os9bfNQ9xnArZX7OhzN+aIh8aK5gmEPJE1JaepPyC0X8vaTBqFiQlK\\n6aRB89RqOUlB86B9vzJca7p7LQKBgQDHg1h9A6X9EkWewW5cSOuScw4FElK8N62v\\n5oVByBZZb/Ys9zP04m0yG7VdRSjk8xyCH5+GDS5m9jTxJdctON2AOPL7de8KOtga\\nJSHivUdDLkt7wSmvblc/JYnNs5+B783gTOpdBrXhV6Wo+QpVw1Pcx15b10WLAs8l\\nMzk7LG27cwKBgDJPorVNCIzB7nL+czrMcfnCPURfsaiGISbwWBJEUO7cCVD6gNcK\\nvb1eSaPSoAcOmJmAn49MbatcNuoFQtyVLQZJ2uvAuk6iQcdfF8BmN9WCL2A1xgWF\\nBoA+/WULpngJZtczvLMxNcac4C5gAtRyY44+ZIQflcAQKDW9S7qGt17xAoGBAJ37\\npLtBg1PU/yoJ81DCMT/DOYvMiZUe5bsO5+BCB2iE3sOWcB7umRb/l+qmVA6Pb7ie\\nP9yPXXoMZbm6hBv8FnFtJwL1zPYlyG9TjfSUevR4mS8CsvaGhjGvkOJA5QKoGDcP\\n0Nke8jDhDX2yzntA84w0lsRUv22nKM5FNIFl2fJ/AoGAOAVtlKRPPi2YrjUqqy6F\\nYr9RXwDZIaHQv9RKzkhPN346zXrYOuAGoL7V7F/MyUH3nX3pzHJDns71+S4Ms5qq\\n6ZjMCu/ic/RsCIoCH5IQsubLpI5bnSsHVt8wLMNR9LwQ/lbRJPWF4LmMnDNJCuC0\\nqJd/bEiNrFhu8IgD6NCT7dQ=\\n-----END PRIVATE KEY-----\\n",\n  "client_email": "search-console-integration-tes@airbyte.iam.gserviceaccount.com",\n  "client_id": "123",\n  "auth_uri": "https://accounts.google.com/o/oauth2/auth",\n  "token_uri": "https://oauth2.googleapis.com/token",\n  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",\n  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/search-console-integration-test%40dairbyte.iam.gserviceaccount.com"\n}',
            "email": "test@example.com",
        },
        "custom_reports": '[{"name": "custom_dimensions", "dimensions": ["date", "country", "device"]}]',
        "custom_reports_array": [{"name": "custom_dimensions", "dimensions": ["date", "country", "device"]}],
    }


@fixture(name="forbidden_error_message_json")
def forbidden_error_message_json():
    return {
        "error": {
            "code": 403,
            "message": "User does not have sufficient permission for site 'https://test-site-test.com/'. See also: https://support.google.com/webmasters/answer/9999999.",
            "errors": [
                {
                    "message": "User does not have sufficient permission for site 'https://test-site-test.com/'. See also: https://support.google.com/webmasters/answer/9999999.",
                    "domain": "global",
                    "reason": "forbidden",
                }
            ],
        }
    }


@fixture(name="bad_aggregation_type")
def bad_aggregation_type():
    return {
        "error": {
            "code": 400,
            "message": "'BY_PROPERTY' is not a valid aggregation type in the context of the request.",
            "errors": [
                {
                    "message": "'BY_PROPERTY' is not a valid aggregation type in the context of the request.",
                    "domain": "global",
                    "reason": "invalidParameter",
                    "location": "aggregation_type",
                    "locationType": "parameter",
                }
            ],
        }
    }


@fixture
def config_gen(config):
    def inner(**kwargs):
        new_config = deepcopy(config)
        # WARNING, no support deep dictionaries
        new_config.update(kwargs)
        return {k: v for k, v in new_config.items() if v is not ...}

    return inner

#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from json import dumps

import pytest
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode

os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


@pytest.fixture
def logger():
    return AirbyteLogger()


@pytest.fixture
def basic_config():
    return {"shop": "test_shop", "credentials": {"auth_method": "api_password", "api_password": "api_password"}}


@pytest.fixture
def auth_config():
    return {
        "shop": "test_shop",
        "start_date": "2023-01-01",
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "authenticator": None,
    }


@pytest.fixture
def catalog_with_streams():
    def _catalog_with_streams(names):
        streams = []
        for name in names:
            streams.append(
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(name=name, json_schema={"type": "object"}),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
            )
        return ConfiguredAirbyteCatalog(streams=streams)

    return _catalog_with_streams


@pytest.fixture
def response_with_bad_json():
    bad_json_str = '{"customers": [{ "field1": "test1", "field2": }]}'
    response = requests.Response()
    response.status_code = 200
    response._content = bad_json_str.encode("utf-8")
    return response


@pytest.fixture
def bulk_error():
    return {
        'data': {
            'bulkOperationRunQuery': {
                'bulkOperation': None, 
                'userErrors': [
                    {
                        'field': "some_field",
                        'message': "something wrong with the requested field.",
                    },
                ]
            }
        }, 
        'extensions': {
            'cost': {
                'requestedQueryCost': 10, 
                'actualQueryCost': 10, 
                'throttleStatus': {
                    'maximumAvailable': 1000.0, 
                    'currentlyAvailable': 990, 
                    'restoreRate': 50.0,
                    }
                }
            }
        }

 
@pytest.fixture
def bulk_error_with_concurrent_job():
    return {
        'data': {
            'bulkOperationRunQuery': {
                'bulkOperation': None, 
                'userErrors': [
                    {
                        'field': None, 
                        'message': "",
                    },
                    {
                        'field': None, 
                        'message': 'A bulk query operation for this app and shop is already in progress: gid://shopify/BulkOperation/4046676525245.',
                    },
                ]
            }
        }, 
        'extensions': {
            'cost': {
                'requestedQueryCost': 10, 
                'actualQueryCost': 10, 
                'throttleStatus': {
                    'maximumAvailable': 1000.0, 
                    'currentlyAvailable': 990, 
                    'restoreRate': 50.0,
                    }
                }
            }
        }


@pytest.fixture
def bulk_successful_response():
    return {
        'data': {
            'bulkOperationRunQuery': {
                'bulkOperation': {
                    'id': 'gid://shopify/BulkOperation/4046733967549', 
                    'status': "CREATED",
                }, 
            'userErrors': [],
            }
        }, 
        'extensions': {
            'cost': {
                'requestedQueryCost': 10, 
                'actualQueryCost': 10, 
                'throttleStatus': {
                    'maximumAvailable': 1000.0, 
                    'currentlyAvailable': 990, 
                    'restoreRate': 50.0,
                    }
                }
            }
        }


@pytest.fixture
def bulk_successful_completed_response():
    return {
        'data': {
            'bulkOperationRunQuery': {
                'bulkOperation': {
                    'id': 'gid://shopify/BulkOperation/4046733967549', 
                    'status': "CREATED",
                    'url': '"https://some_url/response-content-disposition=attachment;+filename="bulk-123456789.jsonl";+filename*=UTF-8''bulk-4047416819901.jsonl&response-content-type=application/jsonl"',
                }, 
            'userErrors': [],
            }
        }, 
        'extensions': {
            'cost': {
                'requestedQueryCost': 10, 
                'actualQueryCost': 10, 
                'throttleStatus': {
                    'maximumAvailable': 1000.0, 
                    'currentlyAvailable': 990, 
                    'restoreRate': 50.0,
                    }
                }
            }
        }


@pytest.fixture
def bulk_job_created_response():
    return {
        'data': {
            'bulkOperationRunQuery': {
                'bulkOperation': {
                    'id': 'gid://shopify/BulkOperation/4046733967549', 
                    'status': "CREATED",
                }, 
            'userErrors': [],
            }
        }, 
        'extensions': {
            'cost': {
                'requestedQueryCost': 10, 
                'actualQueryCost': 10, 
                'throttleStatus': {
                    'maximumAvailable': 1000.0, 
                    'currentlyAvailable': 990, 
                    'restoreRate': 50.0,
                    }
                }
            }
        }


@pytest.fixture
def bulk_job_completed_response():
    return {
        'data': {
            'node': {
                'id': 'gid://shopify/BulkOperation/4047052112061', 
                'status': 'COMPLETED', 
                'errorCode': None, 
                'objectCount': '0', 
                'fileSize': None, 
                'url': 'https://some_url?response-content-disposition=attachment;+filename="bulk-123456789.jsonl";+filename*=UTF-8''bulk-123456789.jsonl&response-content-type=application/jsonl', 
                'partialDataUrl': None,
                }
            }, 
        'extensions': {
            'cost': {
                'requestedQueryCost': 1, 
                'actualQueryCost': 1, 
                'throttleStatus': {
                    'maximumAvailable': 1000.0, 
                    'currentlyAvailable': 999, 
                    'restoreRate': 50.0,
                }
            }
        }
    }


@pytest.fixture
def bulk_job_failed_response():
    return {
        'data': {
            'node': {
                'id': 'gid://shopify/BulkOperation/4047052112061', 
                'status': 'FAILED', 
                'errorCode': None, 
                'objectCount': '0', 
                'fileSize': None, 
                'url': None, 
                'partialDataUrl': None,
                }
            }, 
        'extensions': {
            'cost': {
                'requestedQueryCost': 1, 
                'actualQueryCost': 1, 
                'throttleStatus': {
                    'maximumAvailable': 1000.0, 
                    'currentlyAvailable': 999, 
                    'restoreRate': 50.0,
                }
            }
        }
    }


@pytest.fixture
def bulk_job_timeout_response():
    return {
        'data': {
            'node': {
                'id': 'gid://shopify/BulkOperation/4047052112061', 
                'status': 'TIMEOUT', 
                'errorCode': None, 
                'objectCount': '0', 
                'fileSize': None, 
                'url': None, 
                'partialDataUrl': None,
                }
            }, 
        'extensions': {
            'cost': {
                'requestedQueryCost': 1, 
                'actualQueryCost': 1, 
                'throttleStatus': {
                    'maximumAvailable': 1000.0, 
                    'currentlyAvailable': 999, 
                    'restoreRate': 50.0,
                }
            }
        }
    }
    

@pytest.fixture
def bulk_job_access_denied_response():
    return {
        'data': {
            'node': {
                'id': 'gid://shopify/BulkOperation/4047052112061', 
                'status': 'ACCESS_DENIED', 
                'errorCode': None, 
                'objectCount': '0', 
                'fileSize': None, 
                'url': None, 
                'partialDataUrl': None,
                }
            }, 
        'extensions': {
            'cost': {
                'requestedQueryCost': 1, 
                'actualQueryCost': 1, 
                'throttleStatus': {
                    'maximumAvailable': 1000.0, 
                    'currentlyAvailable': 999, 
                    'restoreRate': 50.0,
                }
            }
        }
    }
    

@pytest.fixture
def bulk_job_unknown_status_response():
    return {
        'data': {
            'node': {
                'id': 'gid://shopify/BulkOperation/4047052112061', 
                'status': None, 
                'errorCode': None, 
                'objectCount': '0', 
                'fileSize': None, 
                'url': None, 
                'partialDataUrl': None,
                }
            }, 
        'extensions': {
            'cost': {
                'requestedQueryCost': 1, 
                'actualQueryCost': 1, 
                'throttleStatus': {
                    'maximumAvailable': 1000.0, 
                    'currentlyAvailable': 999, 
                    'restoreRate': 50.0,
                }
            }
        }
    }
    
    
@pytest.fixture
def jsonl_content_example():
    return dumps(
        {
            "id": "gid://shopify/Metafield/123",
            "__parentId": "gid://shopify/Order/1234567",
            "createdAt": "2023-01-01T01:01:01Z",
            "updatedAt": "2023-01-01T01:01:01Z",
        }
    )
    

@pytest.fixture
def parse_response_expected_result():
    return {
            "id": 123,
            "admin_graphql_api_id": "gid://shopify/Metafield/123",
            "owner_id": 1234567,
            "owner_resource": "order",
            "shop_url": "test_shop",
            "created_at": "2023-01-01T01:01:01+00:00",
            "updated_at": "2023-01-01T01:01:01+00:00",
        }
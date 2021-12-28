# airbyte_api_client.DbMigrationApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**execute_migrations**](DbMigrationApi.md#execute_migrations) | **POST** /v1/db_migrations/migrate | Migrate the database to the latest version
[**list_migrations**](DbMigrationApi.md#list_migrations) | **POST** /v1/db_migrations/list | List all database migrations


# **execute_migrations**
> DbMigrationExecutionRead execute_migrations(db_migration_request_body)

Migrate the database to the latest version

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import db_migration_api
from airbyte_api_client.model.db_migration_request_body import DbMigrationRequestBody
from airbyte_api_client.model.db_migration_execution_read import DbMigrationExecutionRead
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = db_migration_api.DbMigrationApi(api_client)
    db_migration_request_body = DbMigrationRequestBody(
        database="database_example",
    ) # DbMigrationRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Migrate the database to the latest version
        api_response = api_instance.execute_migrations(db_migration_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DbMigrationApi->execute_migrations: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **db_migration_request_body** | [**DbMigrationRequestBody**](DbMigrationRequestBody.md)|  |

### Return type

[**DbMigrationExecutionRead**](DbMigrationExecutionRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |
**404** | Object with given id was not found. |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_migrations**
> DbMigrationReadList list_migrations(db_migration_request_body)

List all database migrations

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import db_migration_api
from airbyte_api_client.model.db_migration_read_list import DbMigrationReadList
from airbyte_api_client.model.db_migration_request_body import DbMigrationRequestBody
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = db_migration_api.DbMigrationApi(api_client)
    db_migration_request_body = DbMigrationRequestBody(
        database="database_example",
    ) # DbMigrationRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # List all database migrations
        api_response = api_instance.list_migrations(db_migration_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DbMigrationApi->list_migrations: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **db_migration_request_body** | [**DbMigrationRequestBody**](DbMigrationRequestBody.md)|  |

### Return type

[**DbMigrationReadList**](DbMigrationReadList.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |
**404** | Object with given id was not found. |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


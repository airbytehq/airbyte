# airbyte_api_client.SchedulerApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**execute_destination_check_connection**](SchedulerApi.md#execute_destination_check_connection) | **POST** /v1/scheduler/destinations/check_connection | Run check connection for a given destination configuration
[**execute_source_check_connection**](SchedulerApi.md#execute_source_check_connection) | **POST** /v1/scheduler/sources/check_connection | Run check connection for a given source configuration
[**execute_source_discover_schema**](SchedulerApi.md#execute_source_discover_schema) | **POST** /v1/scheduler/sources/discover_schema | Run discover schema for a given source a source configuration


# **execute_destination_check_connection**
> CheckConnectionRead execute_destination_check_connection(destination_core_config)

Run check connection for a given destination configuration

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import scheduler_api
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.check_connection_read import CheckConnectionRead
from airbyte_api_client.model.destination_core_config import DestinationCoreConfig
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = scheduler_api.SchedulerApi(api_client)
    destination_core_config = DestinationCoreConfig(
        destination_definition_id="destination_definition_id_example",
        connection_configuration=None,
    ) # DestinationCoreConfig | 

    # example passing only required values which don't have defaults set
    try:
        # Run check connection for a given destination configuration
        api_response = api_instance.execute_destination_check_connection(destination_core_config)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SchedulerApi->execute_destination_check_connection: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_core_config** | [**DestinationCoreConfig**](DestinationCoreConfig.md)|  |

### Return type

[**CheckConnectionRead**](CheckConnectionRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **execute_source_check_connection**
> CheckConnectionRead execute_source_check_connection(source_core_config)

Run check connection for a given source configuration

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import scheduler_api
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.source_core_config import SourceCoreConfig
from airbyte_api_client.model.check_connection_read import CheckConnectionRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = scheduler_api.SchedulerApi(api_client)
    source_core_config = SourceCoreConfig(
        source_definition_id="source_definition_id_example",
        connection_configuration=None,
    ) # SourceCoreConfig | 

    # example passing only required values which don't have defaults set
    try:
        # Run check connection for a given source configuration
        api_response = api_instance.execute_source_check_connection(source_core_config)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SchedulerApi->execute_source_check_connection: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_core_config** | [**SourceCoreConfig**](SourceCoreConfig.md)|  |

### Return type

[**CheckConnectionRead**](CheckConnectionRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **execute_source_discover_schema**
> SourceDiscoverSchemaRead execute_source_discover_schema(source_core_config)

Run discover schema for a given source a source configuration

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import scheduler_api
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.source_core_config import SourceCoreConfig
from airbyte_api_client.model.source_discover_schema_read import SourceDiscoverSchemaRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = scheduler_api.SchedulerApi(api_client)
    source_core_config = SourceCoreConfig(
        source_definition_id="source_definition_id_example",
        connection_configuration=None,
    ) # SourceCoreConfig | 

    # example passing only required values which don't have defaults set
    try:
        # Run discover schema for a given source a source configuration
        api_response = api_instance.execute_source_discover_schema(source_core_config)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SchedulerApi->execute_source_discover_schema: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_core_config** | [**SourceCoreConfig**](SourceCoreConfig.md)|  |

### Return type

[**SourceDiscoverSchemaRead**](SourceDiscoverSchemaRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


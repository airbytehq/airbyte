# airbyte_api_client.LogsApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_logs**](LogsApi.md#get_logs) | **POST** /v1/logs/get | Get logs


# **get_logs**
> file_type get_logs(logs_request_body)

Get logs

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import logs_api
from airbyte_api_client.model.logs_request_body import LogsRequestBody
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
    api_instance = logs_api.LogsApi(api_client)
    logs_request_body = LogsRequestBody(
        log_type=LogType("server"),
    ) # LogsRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Get logs
        api_response = api_instance.get_logs(logs_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling LogsApi->get_logs: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **logs_request_body** | [**LogsRequestBody**](LogsRequestBody.md)|  |

### Return type

**file_type**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: text/plain, application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Returns the log file |  -  |
**404** | Object with given id was not found. |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


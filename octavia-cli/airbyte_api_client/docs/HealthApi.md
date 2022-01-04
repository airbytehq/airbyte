# airbyte_api_client.HealthApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_health_check**](HealthApi.md#get_health_check) | **GET** /v1/health | Health Check


# **get_health_check**
> HealthCheckRead get_health_check()

Health Check

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import health_api
from airbyte_api_client.model.health_check_read import HealthCheckRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = health_api.HealthApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Health Check
        api_response = api_instance.get_health_check()
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling HealthApi->get_health_check: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**HealthCheckRead**](HealthCheckRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


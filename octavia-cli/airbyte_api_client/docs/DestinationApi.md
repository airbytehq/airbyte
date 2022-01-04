# airbyte_api_client.DestinationApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**check_connection_to_destination**](DestinationApi.md#check_connection_to_destination) | **POST** /v1/destinations/check_connection | Check connection to the destination
[**check_connection_to_destination_for_update**](DestinationApi.md#check_connection_to_destination_for_update) | **POST** /v1/destinations/check_connection_for_update | Check connection for a proposed update to a destination
[**create_destination**](DestinationApi.md#create_destination) | **POST** /v1/destinations/create | Create a destination
[**delete_destination**](DestinationApi.md#delete_destination) | **POST** /v1/destinations/delete | Delete the destination
[**get_destination**](DestinationApi.md#get_destination) | **POST** /v1/destinations/get | Get configured destination
[**list_destinations_for_workspace**](DestinationApi.md#list_destinations_for_workspace) | **POST** /v1/destinations/list | List configured destinations for a workspace
[**search_destinations**](DestinationApi.md#search_destinations) | **POST** /v1/destinations/search | Search destinations
[**update_destination**](DestinationApi.md#update_destination) | **POST** /v1/destinations/update | Update a destination


# **check_connection_to_destination**
> CheckConnectionRead check_connection_to_destination(destination_id_request_body)

Check connection to the destination

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_api
from airbyte_api_client.model.destination_id_request_body import DestinationIdRequestBody
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
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
    api_instance = destination_api.DestinationApi(api_client)
    destination_id_request_body = DestinationIdRequestBody(
        destination_id="destination_id_example",
    ) # DestinationIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Check connection to the destination
        api_response = api_instance.check_connection_to_destination(destination_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationApi->check_connection_to_destination: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_id_request_body** | [**DestinationIdRequestBody**](DestinationIdRequestBody.md)|  |

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
**404** | Object with given id was not found. |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **check_connection_to_destination_for_update**
> CheckConnectionRead check_connection_to_destination_for_update(destination_update)

Check connection for a proposed update to a destination

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_api
from airbyte_api_client.model.destination_update import DestinationUpdate
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
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
    api_instance = destination_api.DestinationApi(api_client)
    destination_update = DestinationUpdate(
        destination_id="destination_id_example",
        connection_configuration=None,
        name="name_example",
    ) # DestinationUpdate | 

    # example passing only required values which don't have defaults set
    try:
        # Check connection for a proposed update to a destination
        api_response = api_instance.check_connection_to_destination_for_update(destination_update)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationApi->check_connection_to_destination_for_update: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_update** | [**DestinationUpdate**](DestinationUpdate.md)|  |

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
**404** | Object with given id was not found. |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_destination**
> DestinationRead create_destination(destination_create)

Create a destination

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_api
from airbyte_api_client.model.destination_create import DestinationCreate
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.destination_read import DestinationRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = destination_api.DestinationApi(api_client)
    destination_create = DestinationCreate(
        workspace_id="workspace_id_example",
        name="name_example",
        destination_definition_id="destination_definition_id_example",
        connection_configuration=None,
    ) # DestinationCreate | 

    # example passing only required values which don't have defaults set
    try:
        # Create a destination
        api_response = api_instance.create_destination(destination_create)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationApi->create_destination: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_create** | [**DestinationCreate**](DestinationCreate.md)|  |

### Return type

[**DestinationRead**](DestinationRead.md)

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

# **delete_destination**
> delete_destination(destination_id_request_body)

Delete the destination

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_api
from airbyte_api_client.model.destination_id_request_body import DestinationIdRequestBody
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
    api_instance = destination_api.DestinationApi(api_client)
    destination_id_request_body = DestinationIdRequestBody(
        destination_id="destination_id_example",
    ) # DestinationIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Delete the destination
        api_instance.delete_destination(destination_id_request_body)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationApi->delete_destination: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_id_request_body** | [**DestinationIdRequestBody**](DestinationIdRequestBody.md)|  |

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | The resource was deleted successfully. |  -  |
**404** | Object with given id was not found. |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_destination**
> DestinationRead get_destination(destination_id_request_body)

Get configured destination

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_api
from airbyte_api_client.model.destination_id_request_body import DestinationIdRequestBody
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.destination_read import DestinationRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = destination_api.DestinationApi(api_client)
    destination_id_request_body = DestinationIdRequestBody(
        destination_id="destination_id_example",
    ) # DestinationIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Get configured destination
        api_response = api_instance.get_destination(destination_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationApi->get_destination: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_id_request_body** | [**DestinationIdRequestBody**](DestinationIdRequestBody.md)|  |

### Return type

[**DestinationRead**](DestinationRead.md)

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

# **list_destinations_for_workspace**
> DestinationReadList list_destinations_for_workspace(workspace_id_request_body)

List configured destinations for a workspace

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_api
from airbyte_api_client.model.workspace_id_request_body import WorkspaceIdRequestBody
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.destination_read_list import DestinationReadList
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = destination_api.DestinationApi(api_client)
    workspace_id_request_body = WorkspaceIdRequestBody(
        workspace_id="workspace_id_example",
    ) # WorkspaceIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # List configured destinations for a workspace
        api_response = api_instance.list_destinations_for_workspace(workspace_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationApi->list_destinations_for_workspace: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id_request_body** | [**WorkspaceIdRequestBody**](WorkspaceIdRequestBody.md)|  |

### Return type

[**DestinationReadList**](DestinationReadList.md)

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

# **search_destinations**
> DestinationReadList search_destinations(destination_search)

Search destinations

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_api
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.destination_search import DestinationSearch
from airbyte_api_client.model.destination_read_list import DestinationReadList
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = destination_api.DestinationApi(api_client)
    destination_search = DestinationSearch(
        destination_definition_id="destination_definition_id_example",
        destination_id="destination_id_example",
        workspace_id="workspace_id_example",
        connection_configuration=None,
        name="name_example",
        destination_name="destination_name_example",
    ) # DestinationSearch | 

    # example passing only required values which don't have defaults set
    try:
        # Search destinations
        api_response = api_instance.search_destinations(destination_search)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationApi->search_destinations: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_search** | [**DestinationSearch**](DestinationSearch.md)|  |

### Return type

[**DestinationReadList**](DestinationReadList.md)

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

# **update_destination**
> DestinationRead update_destination(destination_update)

Update a destination

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_api
from airbyte_api_client.model.destination_update import DestinationUpdate
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.destination_read import DestinationRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = destination_api.DestinationApi(api_client)
    destination_update = DestinationUpdate(
        destination_id="destination_id_example",
        connection_configuration=None,
        name="name_example",
    ) # DestinationUpdate | 

    # example passing only required values which don't have defaults set
    try:
        # Update a destination
        api_response = api_instance.update_destination(destination_update)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationApi->update_destination: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_update** | [**DestinationUpdate**](DestinationUpdate.md)|  |

### Return type

[**DestinationRead**](DestinationRead.md)

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


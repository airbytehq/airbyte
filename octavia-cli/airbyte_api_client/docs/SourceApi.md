# airbyte_api_client.SourceApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**check_connection_to_source**](SourceApi.md#check_connection_to_source) | **POST** /v1/sources/check_connection | Check connection to the source
[**check_connection_to_source_for_update**](SourceApi.md#check_connection_to_source_for_update) | **POST** /v1/sources/check_connection_for_update | Check connection for a proposed update to a source
[**create_source**](SourceApi.md#create_source) | **POST** /v1/sources/create | Create a source
[**delete_source**](SourceApi.md#delete_source) | **POST** /v1/sources/delete | Delete a source
[**discover_schema_for_source**](SourceApi.md#discover_schema_for_source) | **POST** /v1/sources/discover_schema | Discover the schema catalog of the source
[**get_source**](SourceApi.md#get_source) | **POST** /v1/sources/get | Get source
[**list_sources_for_workspace**](SourceApi.md#list_sources_for_workspace) | **POST** /v1/sources/list | List sources for workspace
[**search_sources**](SourceApi.md#search_sources) | **POST** /v1/sources/search | Search sources
[**update_source**](SourceApi.md#update_source) | **POST** /v1/sources/update | Update a source


# **check_connection_to_source**
> CheckConnectionRead check_connection_to_source(source_id_request_body)

Check connection to the source

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_api
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody
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
    api_instance = source_api.SourceApi(api_client)
    source_id_request_body = SourceIdRequestBody(
        source_id="source_id_example",
    ) # SourceIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Check connection to the source
        api_response = api_instance.check_connection_to_source(source_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceApi->check_connection_to_source: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_id_request_body** | [**SourceIdRequestBody**](SourceIdRequestBody.md)|  |

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

# **check_connection_to_source_for_update**
> CheckConnectionRead check_connection_to_source_for_update(source_update)

Check connection for a proposed update to a source

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_api
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.check_connection_read import CheckConnectionRead
from airbyte_api_client.model.source_update import SourceUpdate
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = source_api.SourceApi(api_client)
    source_update = SourceUpdate(
        source_id="source_id_example",
        connection_configuration=None,
        name="name_example",
    ) # SourceUpdate | 

    # example passing only required values which don't have defaults set
    try:
        # Check connection for a proposed update to a source
        api_response = api_instance.check_connection_to_source_for_update(source_update)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceApi->check_connection_to_source_for_update: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_update** | [**SourceUpdate**](SourceUpdate.md)|  |

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

# **create_source**
> SourceRead create_source(source_create)

Create a source

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_api
from airbyte_api_client.model.source_create import SourceCreate
from airbyte_api_client.model.source_read import SourceRead
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = source_api.SourceApi(api_client)
    source_create = SourceCreate(
        source_definition_id="source_definition_id_example",
        connection_configuration=None,
        workspace_id="workspace_id_example",
        name="name_example",
    ) # SourceCreate | 

    # example passing only required values which don't have defaults set
    try:
        # Create a source
        api_response = api_instance.create_source(source_create)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceApi->create_source: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_create** | [**SourceCreate**](SourceCreate.md)|  |

### Return type

[**SourceRead**](SourceRead.md)

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

# **delete_source**
> delete_source(source_id_request_body)

Delete a source

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_api
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody
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
    api_instance = source_api.SourceApi(api_client)
    source_id_request_body = SourceIdRequestBody(
        source_id="source_id_example",
    ) # SourceIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Delete a source
        api_instance.delete_source(source_id_request_body)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceApi->delete_source: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_id_request_body** | [**SourceIdRequestBody**](SourceIdRequestBody.md)|  |

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

# **discover_schema_for_source**
> SourceDiscoverSchemaRead discover_schema_for_source(source_id_request_body)

Discover the schema catalog of the source

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_api
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
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
    api_instance = source_api.SourceApi(api_client)
    source_id_request_body = SourceIdRequestBody(
        source_id="source_id_example",
    ) # SourceIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Discover the schema catalog of the source
        api_response = api_instance.discover_schema_for_source(source_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceApi->discover_schema_for_source: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_id_request_body** | [**SourceIdRequestBody**](SourceIdRequestBody.md)|  |

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
**404** | Object with given id was not found. |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_source**
> SourceRead get_source(source_id_request_body)

Get source

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_api
from airbyte_api_client.model.source_read import SourceRead
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody
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
    api_instance = source_api.SourceApi(api_client)
    source_id_request_body = SourceIdRequestBody(
        source_id="source_id_example",
    ) # SourceIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Get source
        api_response = api_instance.get_source(source_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceApi->get_source: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_id_request_body** | [**SourceIdRequestBody**](SourceIdRequestBody.md)|  |

### Return type

[**SourceRead**](SourceRead.md)

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

# **list_sources_for_workspace**
> SourceReadList list_sources_for_workspace(workspace_id_request_body)

List sources for workspace

List sources for workspace. Does not return deleted sources.

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_api
from airbyte_api_client.model.workspace_id_request_body import WorkspaceIdRequestBody
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.source_read_list import SourceReadList
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = source_api.SourceApi(api_client)
    workspace_id_request_body = WorkspaceIdRequestBody(
        workspace_id="workspace_id_example",
    ) # WorkspaceIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # List sources for workspace
        api_response = api_instance.list_sources_for_workspace(workspace_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceApi->list_sources_for_workspace: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id_request_body** | [**WorkspaceIdRequestBody**](WorkspaceIdRequestBody.md)|  |

### Return type

[**SourceReadList**](SourceReadList.md)

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

# **search_sources**
> SourceReadList search_sources(source_search)

Search sources

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_api
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.source_search import SourceSearch
from airbyte_api_client.model.source_read_list import SourceReadList
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = source_api.SourceApi(api_client)
    source_search = SourceSearch(
        source_definition_id="source_definition_id_example",
        source_id="source_id_example",
        workspace_id="workspace_id_example",
        connection_configuration=None,
        name="name_example",
        source_name="source_name_example",
    ) # SourceSearch | 

    # example passing only required values which don't have defaults set
    try:
        # Search sources
        api_response = api_instance.search_sources(source_search)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceApi->search_sources: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_search** | [**SourceSearch**](SourceSearch.md)|  |

### Return type

[**SourceReadList**](SourceReadList.md)

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

# **update_source**
> SourceRead update_source(source_update)

Update a source

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_api
from airbyte_api_client.model.source_read import SourceRead
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.source_update import SourceUpdate
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = source_api.SourceApi(api_client)
    source_update = SourceUpdate(
        source_id="source_id_example",
        connection_configuration=None,
        name="name_example",
    ) # SourceUpdate | 

    # example passing only required values which don't have defaults set
    try:
        # Update a source
        api_response = api_instance.update_source(source_update)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceApi->update_source: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_update** | [**SourceUpdate**](SourceUpdate.md)|  |

### Return type

[**SourceRead**](SourceRead.md)

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


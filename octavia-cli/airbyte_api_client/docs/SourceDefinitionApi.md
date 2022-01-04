# airbyte_api_client.SourceDefinitionApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_source_definition**](SourceDefinitionApi.md#create_source_definition) | **POST** /v1/source_definitions/create | Creates a sourceDefinition
[**delete_source_definition**](SourceDefinitionApi.md#delete_source_definition) | **POST** /v1/source_definitions/delete | Delete a source definition
[**get_source_definition**](SourceDefinitionApi.md#get_source_definition) | **POST** /v1/source_definitions/get | Get source
[**list_latest_source_definitions**](SourceDefinitionApi.md#list_latest_source_definitions) | **POST** /v1/source_definitions/list_latest | List the latest sourceDefinitions Airbyte supports
[**list_source_definitions**](SourceDefinitionApi.md#list_source_definitions) | **POST** /v1/source_definitions/list | List all the sourceDefinitions the current Airbyte deployment is configured to use
[**update_source_definition**](SourceDefinitionApi.md#update_source_definition) | **POST** /v1/source_definitions/update | Update a sourceDefinition


# **create_source_definition**
> SourceDefinitionRead create_source_definition()

Creates a sourceDefinition

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_definition_api
from airbyte_api_client.model.source_definition_create import SourceDefinitionCreate
from airbyte_api_client.model.source_definition_read import SourceDefinitionRead
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
    api_instance = source_definition_api.SourceDefinitionApi(api_client)
    source_definition_create = SourceDefinitionCreate(
        name="name_example",
        docker_repository="docker_repository_example",
        docker_image_tag="docker_image_tag_example",
        documentation_url="documentation_url_example",
        icon="icon_example",
    ) # SourceDefinitionCreate |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Creates a sourceDefinition
        api_response = api_instance.create_source_definition(source_definition_create=source_definition_create)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceDefinitionApi->create_source_definition: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_definition_create** | [**SourceDefinitionCreate**](SourceDefinitionCreate.md)|  | [optional]

### Return type

[**SourceDefinitionRead**](SourceDefinitionRead.md)

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

# **delete_source_definition**
> delete_source_definition(source_definition_id_request_body)

Delete a source definition

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_definition_api
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.source_definition_id_request_body import SourceDefinitionIdRequestBody
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = source_definition_api.SourceDefinitionApi(api_client)
    source_definition_id_request_body = SourceDefinitionIdRequestBody(
        source_definition_id="source_definition_id_example",
    ) # SourceDefinitionIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Delete a source definition
        api_instance.delete_source_definition(source_definition_id_request_body)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceDefinitionApi->delete_source_definition: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_definition_id_request_body** | [**SourceDefinitionIdRequestBody**](SourceDefinitionIdRequestBody.md)|  |

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

# **get_source_definition**
> SourceDefinitionRead get_source_definition(source_definition_id_request_body)

Get source

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_definition_api
from airbyte_api_client.model.source_definition_read import SourceDefinitionRead
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.source_definition_id_request_body import SourceDefinitionIdRequestBody
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = source_definition_api.SourceDefinitionApi(api_client)
    source_definition_id_request_body = SourceDefinitionIdRequestBody(
        source_definition_id="source_definition_id_example",
    ) # SourceDefinitionIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Get source
        api_response = api_instance.get_source_definition(source_definition_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceDefinitionApi->get_source_definition: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_definition_id_request_body** | [**SourceDefinitionIdRequestBody**](SourceDefinitionIdRequestBody.md)|  |

### Return type

[**SourceDefinitionRead**](SourceDefinitionRead.md)

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

# **list_latest_source_definitions**
> SourceDefinitionReadList list_latest_source_definitions()

List the latest sourceDefinitions Airbyte supports

Guaranteed to retrieve the latest information on supported sources.

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_definition_api
from airbyte_api_client.model.source_definition_read_list import SourceDefinitionReadList
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = source_definition_api.SourceDefinitionApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # List the latest sourceDefinitions Airbyte supports
        api_response = api_instance.list_latest_source_definitions()
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceDefinitionApi->list_latest_source_definitions: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**SourceDefinitionReadList**](SourceDefinitionReadList.md)

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

# **list_source_definitions**
> SourceDefinitionReadList list_source_definitions()

List all the sourceDefinitions the current Airbyte deployment is configured to use

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_definition_api
from airbyte_api_client.model.source_definition_read_list import SourceDefinitionReadList
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = source_definition_api.SourceDefinitionApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # List all the sourceDefinitions the current Airbyte deployment is configured to use
        api_response = api_instance.list_source_definitions()
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceDefinitionApi->list_source_definitions: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**SourceDefinitionReadList**](SourceDefinitionReadList.md)

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

# **update_source_definition**
> SourceDefinitionRead update_source_definition()

Update a sourceDefinition

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import source_definition_api
from airbyte_api_client.model.source_definition_read import SourceDefinitionRead
from airbyte_api_client.model.source_definition_update import SourceDefinitionUpdate
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
    api_instance = source_definition_api.SourceDefinitionApi(api_client)
    source_definition_update = SourceDefinitionUpdate(
        source_definition_id="source_definition_id_example",
        docker_image_tag="docker_image_tag_example",
    ) # SourceDefinitionUpdate |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update a sourceDefinition
        api_response = api_instance.update_source_definition(source_definition_update=source_definition_update)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling SourceDefinitionApi->update_source_definition: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_definition_update** | [**SourceDefinitionUpdate**](SourceDefinitionUpdate.md)|  | [optional]

### Return type

[**SourceDefinitionRead**](SourceDefinitionRead.md)

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


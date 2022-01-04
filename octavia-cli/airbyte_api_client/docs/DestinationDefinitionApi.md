# airbyte_api_client.DestinationDefinitionApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_destination_definition**](DestinationDefinitionApi.md#create_destination_definition) | **POST** /v1/destination_definitions/create | Creates a destinationsDefinition
[**delete_destination_definition**](DestinationDefinitionApi.md#delete_destination_definition) | **POST** /v1/destination_definitions/delete | Delete a destination definition
[**get_destination_definition**](DestinationDefinitionApi.md#get_destination_definition) | **POST** /v1/destination_definitions/get | Get destinationDefinition
[**list_destination_definitions**](DestinationDefinitionApi.md#list_destination_definitions) | **POST** /v1/destination_definitions/list | List all the destinationDefinitions the current Airbyte deployment is configured to use
[**list_latest_destination_definitions**](DestinationDefinitionApi.md#list_latest_destination_definitions) | **POST** /v1/destination_definitions/list_latest | List the latest destinationDefinitions Airbyte supports
[**update_destination_definition**](DestinationDefinitionApi.md#update_destination_definition) | **POST** /v1/destination_definitions/update | Update destinationDefinition


# **create_destination_definition**
> DestinationDefinitionRead create_destination_definition()

Creates a destinationsDefinition

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_definition_api
from airbyte_api_client.model.destination_definition_create import DestinationDefinitionCreate
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.destination_definition_read import DestinationDefinitionRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = destination_definition_api.DestinationDefinitionApi(api_client)
    destination_definition_create = DestinationDefinitionCreate(
        name="name_example",
        docker_repository="docker_repository_example",
        docker_image_tag="docker_image_tag_example",
        documentation_url="documentation_url_example",
        icon="icon_example",
    ) # DestinationDefinitionCreate |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Creates a destinationsDefinition
        api_response = api_instance.create_destination_definition(destination_definition_create=destination_definition_create)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationDefinitionApi->create_destination_definition: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_definition_create** | [**DestinationDefinitionCreate**](DestinationDefinitionCreate.md)|  | [optional]

### Return type

[**DestinationDefinitionRead**](DestinationDefinitionRead.md)

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

# **delete_destination_definition**
> delete_destination_definition(destination_definition_id_request_body)

Delete a destination definition

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_definition_api
from airbyte_api_client.model.destination_definition_id_request_body import DestinationDefinitionIdRequestBody
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
    api_instance = destination_definition_api.DestinationDefinitionApi(api_client)
    destination_definition_id_request_body = DestinationDefinitionIdRequestBody(
        destination_definition_id="destination_definition_id_example",
    ) # DestinationDefinitionIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Delete a destination definition
        api_instance.delete_destination_definition(destination_definition_id_request_body)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationDefinitionApi->delete_destination_definition: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_definition_id_request_body** | [**DestinationDefinitionIdRequestBody**](DestinationDefinitionIdRequestBody.md)|  |

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

# **get_destination_definition**
> DestinationDefinitionRead get_destination_definition(destination_definition_id_request_body)

Get destinationDefinition

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_definition_api
from airbyte_api_client.model.destination_definition_id_request_body import DestinationDefinitionIdRequestBody
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.destination_definition_read import DestinationDefinitionRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = destination_definition_api.DestinationDefinitionApi(api_client)
    destination_definition_id_request_body = DestinationDefinitionIdRequestBody(
        destination_definition_id="destination_definition_id_example",
    ) # DestinationDefinitionIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Get destinationDefinition
        api_response = api_instance.get_destination_definition(destination_definition_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationDefinitionApi->get_destination_definition: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_definition_id_request_body** | [**DestinationDefinitionIdRequestBody**](DestinationDefinitionIdRequestBody.md)|  |

### Return type

[**DestinationDefinitionRead**](DestinationDefinitionRead.md)

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

# **list_destination_definitions**
> DestinationDefinitionReadList list_destination_definitions()

List all the destinationDefinitions the current Airbyte deployment is configured to use

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_definition_api
from airbyte_api_client.model.destination_definition_read_list import DestinationDefinitionReadList
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = destination_definition_api.DestinationDefinitionApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # List all the destinationDefinitions the current Airbyte deployment is configured to use
        api_response = api_instance.list_destination_definitions()
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationDefinitionApi->list_destination_definitions: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**DestinationDefinitionReadList**](DestinationDefinitionReadList.md)

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

# **list_latest_destination_definitions**
> DestinationDefinitionReadList list_latest_destination_definitions()

List the latest destinationDefinitions Airbyte supports

Guaranteed to retrieve the latest information on supported destinations.

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_definition_api
from airbyte_api_client.model.destination_definition_read_list import DestinationDefinitionReadList
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = destination_definition_api.DestinationDefinitionApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # List the latest destinationDefinitions Airbyte supports
        api_response = api_instance.list_latest_destination_definitions()
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationDefinitionApi->list_latest_destination_definitions: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**DestinationDefinitionReadList**](DestinationDefinitionReadList.md)

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

# **update_destination_definition**
> DestinationDefinitionRead update_destination_definition(destination_definition_update)

Update destinationDefinition

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import destination_definition_api
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.destination_definition_update import DestinationDefinitionUpdate
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.destination_definition_read import DestinationDefinitionRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = destination_definition_api.DestinationDefinitionApi(api_client)
    destination_definition_update = DestinationDefinitionUpdate(
        destination_definition_id="destination_definition_id_example",
        docker_image_tag="docker_image_tag_example",
    ) # DestinationDefinitionUpdate | 

    # example passing only required values which don't have defaults set
    try:
        # Update destinationDefinition
        api_response = api_instance.update_destination_definition(destination_definition_update)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DestinationDefinitionApi->update_destination_definition: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_definition_update** | [**DestinationDefinitionUpdate**](DestinationDefinitionUpdate.md)|  |

### Return type

[**DestinationDefinitionRead**](DestinationDefinitionRead.md)

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


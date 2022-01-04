# airbyte_api_client.OperationApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**check_operation**](OperationApi.md#check_operation) | **POST** /v1/operations/check | Check if an operation to be created is valid
[**create_operation**](OperationApi.md#create_operation) | **POST** /v1/operations/create | Create an operation to be applied as part of a connection pipeline
[**delete_operation**](OperationApi.md#delete_operation) | **POST** /v1/operations/delete | Delete an operation
[**get_operation**](OperationApi.md#get_operation) | **POST** /v1/operations/get | Returns an operation
[**list_operations_for_connection**](OperationApi.md#list_operations_for_connection) | **POST** /v1/operations/list | Returns all operations for a connection.
[**update_operation**](OperationApi.md#update_operation) | **POST** /v1/operations/update | Update an operation


# **check_operation**
> CheckOperationRead check_operation(operator_configuration)

Check if an operation to be created is valid

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import operation_api
from airbyte_api_client.model.check_operation_read import CheckOperationRead
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.operator_configuration import OperatorConfiguration
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = operation_api.OperationApi(api_client)
    operator_configuration = OperatorConfiguration(
        operator_type=OperatorType("normalization"),
        normalization=OperatorNormalization(
            option="basic",
        ),
        dbt=OperatorDbt(
            git_repo_url="git_repo_url_example",
            git_repo_branch="git_repo_branch_example",
            docker_image="docker_image_example",
            dbt_arguments="dbt_arguments_example",
        ),
    ) # OperatorConfiguration | 

    # example passing only required values which don't have defaults set
    try:
        # Check if an operation to be created is valid
        api_response = api_instance.check_operation(operator_configuration)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling OperationApi->check_operation: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operator_configuration** | [**OperatorConfiguration**](OperatorConfiguration.md)|  |

### Return type

[**CheckOperationRead**](CheckOperationRead.md)

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

# **create_operation**
> OperationRead create_operation(operation_create)

Create an operation to be applied as part of a connection pipeline

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import operation_api
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.operation_create import OperationCreate
from airbyte_api_client.model.operation_read import OperationRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = operation_api.OperationApi(api_client)
    operation_create = OperationCreate(
        workspace_id="workspace_id_example",
        name="name_example",
        operator_configuration=OperatorConfiguration(
            operator_type=OperatorType("normalization"),
            normalization=OperatorNormalization(
                option="basic",
            ),
            dbt=OperatorDbt(
                git_repo_url="git_repo_url_example",
                git_repo_branch="git_repo_branch_example",
                docker_image="docker_image_example",
                dbt_arguments="dbt_arguments_example",
            ),
        ),
    ) # OperationCreate | 

    # example passing only required values which don't have defaults set
    try:
        # Create an operation to be applied as part of a connection pipeline
        api_response = api_instance.create_operation(operation_create)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling OperationApi->create_operation: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operation_create** | [**OperationCreate**](OperationCreate.md)|  |

### Return type

[**OperationRead**](OperationRead.md)

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

# **delete_operation**
> delete_operation(operation_id_request_body)

Delete an operation

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import operation_api
from airbyte_api_client.model.operation_id_request_body import OperationIdRequestBody
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
    api_instance = operation_api.OperationApi(api_client)
    operation_id_request_body = OperationIdRequestBody(
        operation_id="operation_id_example",
    ) # OperationIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Delete an operation
        api_instance.delete_operation(operation_id_request_body)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling OperationApi->delete_operation: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operation_id_request_body** | [**OperationIdRequestBody**](OperationIdRequestBody.md)|  |

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

# **get_operation**
> OperationRead get_operation(operation_id_request_body)

Returns an operation

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import operation_api
from airbyte_api_client.model.operation_id_request_body import OperationIdRequestBody
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.operation_read import OperationRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = operation_api.OperationApi(api_client)
    operation_id_request_body = OperationIdRequestBody(
        operation_id="operation_id_example",
    ) # OperationIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Returns an operation
        api_response = api_instance.get_operation(operation_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling OperationApi->get_operation: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operation_id_request_body** | [**OperationIdRequestBody**](OperationIdRequestBody.md)|  |

### Return type

[**OperationRead**](OperationRead.md)

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

# **list_operations_for_connection**
> OperationReadList list_operations_for_connection(connection_id_request_body)

Returns all operations for a connection.

List operations for connection.

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import operation_api
from airbyte_api_client.model.connection_id_request_body import ConnectionIdRequestBody
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.operation_read_list import OperationReadList
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = operation_api.OperationApi(api_client)
    connection_id_request_body = ConnectionIdRequestBody(
        connection_id="connection_id_example",
    ) # ConnectionIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Returns all operations for a connection.
        api_response = api_instance.list_operations_for_connection(connection_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling OperationApi->list_operations_for_connection: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id_request_body** | [**ConnectionIdRequestBody**](ConnectionIdRequestBody.md)|  |

### Return type

[**OperationReadList**](OperationReadList.md)

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

# **update_operation**
> OperationRead update_operation(operation_update)

Update an operation

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import operation_api
from airbyte_api_client.model.operation_update import OperationUpdate
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.operation_read import OperationRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = operation_api.OperationApi(api_client)
    operation_update = OperationUpdate(
        operation_id="operation_id_example",
        name="name_example",
        operator_configuration=OperatorConfiguration(
            operator_type=OperatorType("normalization"),
            normalization=OperatorNormalization(
                option="basic",
            ),
            dbt=OperatorDbt(
                git_repo_url="git_repo_url_example",
                git_repo_branch="git_repo_branch_example",
                docker_image="docker_image_example",
                dbt_arguments="dbt_arguments_example",
            ),
        ),
    ) # OperationUpdate | 

    # example passing only required values which don't have defaults set
    try:
        # Update an operation
        api_response = api_instance.update_operation(operation_update)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling OperationApi->update_operation: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operation_update** | [**OperationUpdate**](OperationUpdate.md)|  |

### Return type

[**OperationRead**](OperationRead.md)

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


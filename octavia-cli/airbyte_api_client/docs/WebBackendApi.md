# airbyte_api_client.WebBackendApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**web_backend_create_connection**](WebBackendApi.md#web_backend_create_connection) | **POST** /v1/web_backend/connections/create | Create a connection
[**web_backend_get_connection**](WebBackendApi.md#web_backend_get_connection) | **POST** /v1/web_backend/connections/get | Get a connection
[**web_backend_list_all_connections_for_workspace**](WebBackendApi.md#web_backend_list_all_connections_for_workspace) | **POST** /v1/web_backend/connections/list_all | Returns all connections for a workspace.
[**web_backend_list_connections_for_workspace**](WebBackendApi.md#web_backend_list_connections_for_workspace) | **POST** /v1/web_backend/connections/list | Returns all non-deleted connections for a workspace.
[**web_backend_search_connections**](WebBackendApi.md#web_backend_search_connections) | **POST** /v1/web_backend/connections/search | Search connections
[**web_backend_update_connection**](WebBackendApi.md#web_backend_update_connection) | **POST** /v1/web_backend/connections/update | Update a connection


# **web_backend_create_connection**
> WebBackendConnectionRead web_backend_create_connection(web_backend_connection_create)

Create a connection

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import web_backend_api
from airbyte_api_client.model.web_backend_connection_read import WebBackendConnectionRead
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.web_backend_connection_create import WebBackendConnectionCreate
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = web_backend_api.WebBackendApi(api_client)
    web_backend_connection_create = WebBackendConnectionCreate(
        name="name_example",
        namespace_definition=NamespaceDefinitionType("source"),
        namespace_format="${SOURCE_NAMESPACE}",
        prefix="prefix_example",
        source_id="source_id_example",
        destination_id="destination_id_example",
        operation_ids=[
            "operation_ids_example",
        ],
        sync_catalog=AirbyteCatalog(
            streams=[
                AirbyteStreamAndConfiguration(
                    stream=AirbyteStream(
                        name="name_example",
                        json_schema={},
                        supported_sync_modes=[
                            SyncMode("full_refresh"),
                        ],
                        source_defined_cursor=True,
                        default_cursor_field=[
                            "default_cursor_field_example",
                        ],
                        source_defined_primary_key=[
                            [
                                "string_example",
                            ],
                        ],
                        namespace="namespace_example",
                    ),
                    config=AirbyteStreamConfiguration(
                        sync_mode=SyncMode("full_refresh"),
                        cursor_field=[
                            "cursor_field_example",
                        ],
                        destination_sync_mode=DestinationSyncMode("append"),
                        primary_key=[
                            [
                                "string_example",
                            ],
                        ],
                        alias_name="alias_name_example",
                        selected=True,
                    ),
                ),
            ],
        ),
        schedule=ConnectionSchedule(
            units=1,
            time_unit="minutes",
        ),
        status=ConnectionStatus("active"),
        resource_requirements=ResourceRequirements(
            cpu_request="cpu_request_example",
            cpu_limit="cpu_limit_example",
            memory_request="memory_request_example",
            memory_limit="memory_limit_example",
        ),
        operations=[
            OperationCreate(
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
            ),
        ],
    ) # WebBackendConnectionCreate | 

    # example passing only required values which don't have defaults set
    try:
        # Create a connection
        api_response = api_instance.web_backend_create_connection(web_backend_connection_create)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WebBackendApi->web_backend_create_connection: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **web_backend_connection_create** | [**WebBackendConnectionCreate**](WebBackendConnectionCreate.md)|  |

### Return type

[**WebBackendConnectionRead**](WebBackendConnectionRead.md)

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

# **web_backend_get_connection**
> WebBackendConnectionRead web_backend_get_connection(web_backend_connection_request_body)

Get a connection

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import web_backend_api
from airbyte_api_client.model.web_backend_connection_request_body import WebBackendConnectionRequestBody
from airbyte_api_client.model.web_backend_connection_read import WebBackendConnectionRead
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
    api_instance = web_backend_api.WebBackendApi(api_client)
    web_backend_connection_request_body = WebBackendConnectionRequestBody(
        with_refreshed_catalog=True,
        connection_id="connection_id_example",
    ) # WebBackendConnectionRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Get a connection
        api_response = api_instance.web_backend_get_connection(web_backend_connection_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WebBackendApi->web_backend_get_connection: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **web_backend_connection_request_body** | [**WebBackendConnectionRequestBody**](WebBackendConnectionRequestBody.md)|  |

### Return type

[**WebBackendConnectionRead**](WebBackendConnectionRead.md)

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

# **web_backend_list_all_connections_for_workspace**
> WebBackendConnectionReadList web_backend_list_all_connections_for_workspace(workspace_id_request_body)

Returns all connections for a workspace.

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import web_backend_api
from airbyte_api_client.model.workspace_id_request_body import WorkspaceIdRequestBody
from airbyte_api_client.model.web_backend_connection_read_list import WebBackendConnectionReadList
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
    api_instance = web_backend_api.WebBackendApi(api_client)
    workspace_id_request_body = WorkspaceIdRequestBody(
        workspace_id="workspace_id_example",
    ) # WorkspaceIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Returns all connections for a workspace.
        api_response = api_instance.web_backend_list_all_connections_for_workspace(workspace_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WebBackendApi->web_backend_list_all_connections_for_workspace: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id_request_body** | [**WorkspaceIdRequestBody**](WorkspaceIdRequestBody.md)|  |

### Return type

[**WebBackendConnectionReadList**](WebBackendConnectionReadList.md)

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

# **web_backend_list_connections_for_workspace**
> WebBackendConnectionReadList web_backend_list_connections_for_workspace(workspace_id_request_body)

Returns all non-deleted connections for a workspace.

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import web_backend_api
from airbyte_api_client.model.workspace_id_request_body import WorkspaceIdRequestBody
from airbyte_api_client.model.web_backend_connection_read_list import WebBackendConnectionReadList
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
    api_instance = web_backend_api.WebBackendApi(api_client)
    workspace_id_request_body = WorkspaceIdRequestBody(
        workspace_id="workspace_id_example",
    ) # WorkspaceIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Returns all non-deleted connections for a workspace.
        api_response = api_instance.web_backend_list_connections_for_workspace(workspace_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WebBackendApi->web_backend_list_connections_for_workspace: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id_request_body** | [**WorkspaceIdRequestBody**](WorkspaceIdRequestBody.md)|  |

### Return type

[**WebBackendConnectionReadList**](WebBackendConnectionReadList.md)

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

# **web_backend_search_connections**
> WebBackendConnectionReadList web_backend_search_connections(web_backend_connection_search)

Search connections

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import web_backend_api
from airbyte_api_client.model.web_backend_connection_search import WebBackendConnectionSearch
from airbyte_api_client.model.web_backend_connection_read_list import WebBackendConnectionReadList
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
    api_instance = web_backend_api.WebBackendApi(api_client)
    web_backend_connection_search = WebBackendConnectionSearch(
        connection_id="connection_id_example",
        name="name_example",
        namespace_definition=NamespaceDefinitionType("source"),
        namespace_format="${SOURCE_NAMESPACE}",
        prefix="prefix_example",
        source_id="source_id_example",
        destination_id="destination_id_example",
        schedule=ConnectionSchedule(
            units=1,
            time_unit="minutes",
        ),
        status=ConnectionStatus("active"),
        source=SourceSearch(
            source_definition_id="source_definition_id_example",
            source_id="source_id_example",
            workspace_id="workspace_id_example",
            connection_configuration=None,
            name="name_example",
            source_name="source_name_example",
        ),
        destination=DestinationSearch(
            destination_definition_id="destination_definition_id_example",
            destination_id="destination_id_example",
            workspace_id="workspace_id_example",
            connection_configuration=None,
            name="name_example",
            destination_name="destination_name_example",
        ),
    ) # WebBackendConnectionSearch | 

    # example passing only required values which don't have defaults set
    try:
        # Search connections
        api_response = api_instance.web_backend_search_connections(web_backend_connection_search)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WebBackendApi->web_backend_search_connections: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **web_backend_connection_search** | [**WebBackendConnectionSearch**](WebBackendConnectionSearch.md)|  |

### Return type

[**WebBackendConnectionReadList**](WebBackendConnectionReadList.md)

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

# **web_backend_update_connection**
> WebBackendConnectionRead web_backend_update_connection(web_backend_connection_update)

Update a connection

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import web_backend_api
from airbyte_api_client.model.web_backend_connection_read import WebBackendConnectionRead
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.web_backend_connection_update import WebBackendConnectionUpdate
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = web_backend_api.WebBackendApi(api_client)
    web_backend_connection_update = WebBackendConnectionUpdate(
        connection_id="connection_id_example",
        namespace_definition=NamespaceDefinitionType("source"),
        namespace_format="${SOURCE_NAMESPACE}",
        prefix="prefix_example",
        operation_ids=[
            "operation_ids_example",
        ],
        sync_catalog=AirbyteCatalog(
            streams=[
                AirbyteStreamAndConfiguration(
                    stream=AirbyteStream(
                        name="name_example",
                        json_schema={},
                        supported_sync_modes=[
                            SyncMode("full_refresh"),
                        ],
                        source_defined_cursor=True,
                        default_cursor_field=[
                            "default_cursor_field_example",
                        ],
                        source_defined_primary_key=[
                            [
                                "string_example",
                            ],
                        ],
                        namespace="namespace_example",
                    ),
                    config=AirbyteStreamConfiguration(
                        sync_mode=SyncMode("full_refresh"),
                        cursor_field=[
                            "cursor_field_example",
                        ],
                        destination_sync_mode=DestinationSyncMode("append"),
                        primary_key=[
                            [
                                "string_example",
                            ],
                        ],
                        alias_name="alias_name_example",
                        selected=True,
                    ),
                ),
            ],
        ),
        schedule=ConnectionSchedule(
            units=1,
            time_unit="minutes",
        ),
        status=ConnectionStatus("active"),
        resource_requirements=ResourceRequirements(
            cpu_request="cpu_request_example",
            cpu_limit="cpu_limit_example",
            memory_request="memory_request_example",
            memory_limit="memory_limit_example",
        ),
        with_refreshed_catalog=True,
        operations=[
            WebBackendOperationCreateOrUpdate(
                operation_id="operation_id_example",
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
            ),
        ],
    ) # WebBackendConnectionUpdate | 

    # example passing only required values which don't have defaults set
    try:
        # Update a connection
        api_response = api_instance.web_backend_update_connection(web_backend_connection_update)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WebBackendApi->web_backend_update_connection: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **web_backend_connection_update** | [**WebBackendConnectionUpdate**](WebBackendConnectionUpdate.md)|  |

### Return type

[**WebBackendConnectionRead**](WebBackendConnectionRead.md)

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


# airbyte_api_client.WorkspaceApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_workspace**](WorkspaceApi.md#create_workspace) | **POST** /v1/workspaces/create | Creates a workspace
[**delete_workspace**](WorkspaceApi.md#delete_workspace) | **POST** /v1/workspaces/delete | Deletes a workspace
[**get_workspace**](WorkspaceApi.md#get_workspace) | **POST** /v1/workspaces/get | Find workspace by ID
[**get_workspace_by_slug**](WorkspaceApi.md#get_workspace_by_slug) | **POST** /v1/workspaces/get_by_slug | Find workspace by slug
[**list_workspaces**](WorkspaceApi.md#list_workspaces) | **POST** /v1/workspaces/list | List all workspaces registered in the current Airbyte deployment
[**update_workspace**](WorkspaceApi.md#update_workspace) | **POST** /v1/workspaces/update | Update workspace state
[**update_workspace_feedback**](WorkspaceApi.md#update_workspace_feedback) | **POST** /v1/workspaces/tag_feedback_status_as_done | Update workspace feedback state


# **create_workspace**
> WorkspaceRead create_workspace(workspace_create)

Creates a workspace

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import workspace_api
from airbyte_api_client.model.workspace_read import WorkspaceRead
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.workspace_create import WorkspaceCreate
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = workspace_api.WorkspaceApi(api_client)
    workspace_create = WorkspaceCreate(
        email="email_example",
        anonymous_data_collection=True,
        name="name_example",
        news=True,
        security_updates=True,
        notifications=[
            Notification(
                notification_type=NotificationType("slack"),
                send_on_success=False,
                send_on_failure=True,
                slack_configuration=SlackNotificationConfiguration(
                    webhook="webhook_example",
                ),
            ),
        ],
        display_setup_wizard=True,
    ) # WorkspaceCreate | 

    # example passing only required values which don't have defaults set
    try:
        # Creates a workspace
        api_response = api_instance.create_workspace(workspace_create)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WorkspaceApi->create_workspace: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_create** | [**WorkspaceCreate**](WorkspaceCreate.md)|  |

### Return type

[**WorkspaceRead**](WorkspaceRead.md)

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

# **delete_workspace**
> delete_workspace(workspace_id_request_body)

Deletes a workspace

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import workspace_api
from airbyte_api_client.model.workspace_id_request_body import WorkspaceIdRequestBody
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
    api_instance = workspace_api.WorkspaceApi(api_client)
    workspace_id_request_body = WorkspaceIdRequestBody(
        workspace_id="workspace_id_example",
    ) # WorkspaceIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Deletes a workspace
        api_instance.delete_workspace(workspace_id_request_body)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WorkspaceApi->delete_workspace: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id_request_body** | [**WorkspaceIdRequestBody**](WorkspaceIdRequestBody.md)|  |

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

# **get_workspace**
> WorkspaceRead get_workspace(workspace_id_request_body)

Find workspace by ID

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import workspace_api
from airbyte_api_client.model.workspace_read import WorkspaceRead
from airbyte_api_client.model.workspace_id_request_body import WorkspaceIdRequestBody
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
    api_instance = workspace_api.WorkspaceApi(api_client)
    workspace_id_request_body = WorkspaceIdRequestBody(
        workspace_id="workspace_id_example",
    ) # WorkspaceIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Find workspace by ID
        api_response = api_instance.get_workspace(workspace_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WorkspaceApi->get_workspace: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id_request_body** | [**WorkspaceIdRequestBody**](WorkspaceIdRequestBody.md)|  |

### Return type

[**WorkspaceRead**](WorkspaceRead.md)

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

# **get_workspace_by_slug**
> WorkspaceRead get_workspace_by_slug(slug_request_body)

Find workspace by slug

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import workspace_api
from airbyte_api_client.model.workspace_read import WorkspaceRead
from airbyte_api_client.model.slug_request_body import SlugRequestBody
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
    api_instance = workspace_api.WorkspaceApi(api_client)
    slug_request_body = SlugRequestBody(
        slug="slug_example",
    ) # SlugRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Find workspace by slug
        api_response = api_instance.get_workspace_by_slug(slug_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WorkspaceApi->get_workspace_by_slug: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **slug_request_body** | [**SlugRequestBody**](SlugRequestBody.md)|  |

### Return type

[**WorkspaceRead**](WorkspaceRead.md)

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

# **list_workspaces**
> WorkspaceReadList list_workspaces()

List all workspaces registered in the current Airbyte deployment

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import workspace_api
from airbyte_api_client.model.workspace_read_list import WorkspaceReadList
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = workspace_api.WorkspaceApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # List all workspaces registered in the current Airbyte deployment
        api_response = api_instance.list_workspaces()
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WorkspaceApi->list_workspaces: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**WorkspaceReadList**](WorkspaceReadList.md)

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

# **update_workspace**
> WorkspaceRead update_workspace(workspace_update)

Update workspace state

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import workspace_api
from airbyte_api_client.model.workspace_read import WorkspaceRead
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.workspace_update import WorkspaceUpdate
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = workspace_api.WorkspaceApi(api_client)
    workspace_update = WorkspaceUpdate(
        workspace_id="workspace_id_example",
        email="email_example",
        initial_setup_complete=True,
        display_setup_wizard=True,
        anonymous_data_collection=True,
        news=True,
        security_updates=True,
        notifications=[
            Notification(
                notification_type=NotificationType("slack"),
                send_on_success=False,
                send_on_failure=True,
                slack_configuration=SlackNotificationConfiguration(
                    webhook="webhook_example",
                ),
            ),
        ],
    ) # WorkspaceUpdate | 

    # example passing only required values which don't have defaults set
    try:
        # Update workspace state
        api_response = api_instance.update_workspace(workspace_update)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WorkspaceApi->update_workspace: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_update** | [**WorkspaceUpdate**](WorkspaceUpdate.md)|  |

### Return type

[**WorkspaceRead**](WorkspaceRead.md)

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

# **update_workspace_feedback**
> update_workspace_feedback(workspace_give_feedback)

Update workspace feedback state

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import workspace_api
from airbyte_api_client.model.workspace_give_feedback import WorkspaceGiveFeedback
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
    api_instance = workspace_api.WorkspaceApi(api_client)
    workspace_give_feedback = WorkspaceGiveFeedback(
        workspace_id="workspace_id_example",
    ) # WorkspaceGiveFeedback | 

    # example passing only required values which don't have defaults set
    try:
        # Update workspace feedback state
        api_instance.update_workspace_feedback(workspace_give_feedback)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling WorkspaceApi->update_workspace_feedback: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_give_feedback** | [**WorkspaceGiveFeedback**](WorkspaceGiveFeedback.md)|  |

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
**204** | The feedback state has been properly updated |  -  |
**404** | Object with given id was not found. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


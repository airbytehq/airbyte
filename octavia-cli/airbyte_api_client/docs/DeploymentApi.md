# airbyte_api_client.DeploymentApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**export_archive**](DeploymentApi.md#export_archive) | **POST** /v1/deployment/export | Export Airbyte Configuration and Data Archive
[**export_workspace**](DeploymentApi.md#export_workspace) | **POST** /v1/deployment/export_workspace | Export Airbyte Workspace Configuration
[**import_archive**](DeploymentApi.md#import_archive) | **POST** /v1/deployment/import | Import Airbyte Configuration and Data Archive
[**import_into_workspace**](DeploymentApi.md#import_into_workspace) | **POST** /v1/deployment/import_into_workspace | Import Airbyte Configuration into Workspace (this operation might change ids of imported configurations). Note, in order to use this api endpoint, you might need to upload a temporary archive resource with &#39;deployment/upload_archive_resource&#39; first 
[**upload_archive_resource**](DeploymentApi.md#upload_archive_resource) | **POST** /v1/deployment/upload_archive_resource | Upload a GZIP archive tarball and stage it in the server&#39;s cache as a temporary resource


# **export_archive**
> file_type export_archive()

Export Airbyte Configuration and Data Archive

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import deployment_api
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = deployment_api.DeploymentApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Export Airbyte Configuration and Data Archive
        api_response = api_instance.export_archive()
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DeploymentApi->export_archive: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

**file_type**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/x-gzip


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_workspace**
> file_type export_workspace(workspace_id_request_body)

Export Airbyte Workspace Configuration

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import deployment_api
from airbyte_api_client.model.workspace_id_request_body import WorkspaceIdRequestBody
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = deployment_api.DeploymentApi(api_client)
    workspace_id_request_body = WorkspaceIdRequestBody(
        workspace_id="workspace_id_example",
    ) # WorkspaceIdRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Export Airbyte Workspace Configuration
        api_response = api_instance.export_workspace(workspace_id_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DeploymentApi->export_workspace: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id_request_body** | [**WorkspaceIdRequestBody**](WorkspaceIdRequestBody.md)|  |

### Return type

**file_type**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/x-gzip


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **import_archive**
> ImportRead import_archive(body)

Import Airbyte Configuration and Data Archive

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import deployment_api
from airbyte_api_client.model.import_read import ImportRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = deployment_api.DeploymentApi(api_client)
    body = open('/path/to/file', 'rb') # file_type | 

    # example passing only required values which don't have defaults set
    try:
        # Import Airbyte Configuration and Data Archive
        api_response = api_instance.import_archive(body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DeploymentApi->import_archive: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **file_type**|  |

### Return type

[**ImportRead**](ImportRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-gzip
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **import_into_workspace**
> ImportRead import_into_workspace(import_request_body)

Import Airbyte Configuration into Workspace (this operation might change ids of imported configurations). Note, in order to use this api endpoint, you might need to upload a temporary archive resource with 'deployment/upload_archive_resource' first 

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import deployment_api
from airbyte_api_client.model.import_request_body import ImportRequestBody
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.import_read import ImportRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = deployment_api.DeploymentApi(api_client)
    import_request_body = ImportRequestBody(
        resource_id="resource_id_example",
        workspace_id="workspace_id_example",
    ) # ImportRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Import Airbyte Configuration into Workspace (this operation might change ids of imported configurations). Note, in order to use this api endpoint, you might need to upload a temporary archive resource with 'deployment/upload_archive_resource' first 
        api_response = api_instance.import_into_workspace(import_request_body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DeploymentApi->import_into_workspace: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **import_request_body** | [**ImportRequestBody**](ImportRequestBody.md)|  |

### Return type

[**ImportRead**](ImportRead.md)

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_archive_resource**
> UploadRead upload_archive_resource(body)

Upload a GZIP archive tarball and stage it in the server's cache as a temporary resource

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import deployment_api
from airbyte_api_client.model.upload_read import UploadRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = deployment_api.DeploymentApi(api_client)
    body = open('/path/to/file', 'rb') # file_type | 

    # example passing only required values which don't have defaults set
    try:
        # Upload a GZIP archive tarball and stage it in the server's cache as a temporary resource
        api_response = api_instance.upload_archive_resource(body)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling DeploymentApi->upload_archive_resource: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **file_type**|  |

### Return type

[**UploadRead**](UploadRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-gzip
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


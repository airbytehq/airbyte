# WebBackendApi

All URIs are relative to *https://virtserver.swaggerhub.com/cgardens6/dataline/1.0.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**webBackendGetConnection**](WebBackendApi.md#webBackendGetConnection) | **POST** /v1/web_backend/connections/get | Get a connection
[**webBackendListConnectionsForWorkspace**](WebBackendApi.md#webBackendListConnectionsForWorkspace) | **POST** /v1/web_backend/connections/list | Returns all connections for a workspace.


<a name="webBackendGetConnection"></a>
# **webBackendGetConnection**
> WbConnectionRead webBackendGetConnection(connectionIdRequestBody)

Get a connection

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connectionIdRequestBody** | [**ConnectionIdRequestBody**](../io.dataline.api.client.model/ConnectionIdRequestBody.md)|  |

### Return type

[**WbConnectionRead**](../io.dataline.api.client.model/WbConnectionRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="webBackendListConnectionsForWorkspace"></a>
# **webBackendListConnectionsForWorkspace**
> WbConnectionReadList webBackendListConnectionsForWorkspace(workspaceIdRequestBody)

Returns all connections for a workspace.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspaceIdRequestBody** | [**WorkspaceIdRequestBody**](../io.dataline.api.client.model/WorkspaceIdRequestBody.md)|  |

### Return type

[**WbConnectionReadList**](../io.dataline.api.client.model/WbConnectionReadList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


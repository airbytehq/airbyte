# ConnectionApi

All URIs are relative to *https://virtserver.swaggerhub.com/cgardens6/dataline/1.0.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createConnection**](ConnectionApi.md#createConnection) | **POST** /v1/connections/create | Create a connection between a source implementation and a destination implementation
[**getConnection**](ConnectionApi.md#getConnection) | **POST** /v1/connections/get | Get a connection
[**listConnectionsForWorkspace**](ConnectionApi.md#listConnectionsForWorkspace) | **POST** /v1/connections/list | Returns all connections for a workspace.
[**syncConnection**](ConnectionApi.md#syncConnection) | **POST** /v1/connections/sync | Trigger a manual sync of the connection
[**updateConnection**](ConnectionApi.md#updateConnection) | **POST** /v1/connections/update | Updated a connection status


<a name="createConnection"></a>
# **createConnection**
> ConnectionRead createConnection(connectionCreate)

Create a connection between a source implementation and a destination implementation

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connectionCreate** | [**ConnectionCreate**](../io.dataline.api.client.model/ConnectionCreate.md)|  |

### Return type

[**ConnectionRead**](../io.dataline.api.client.model/ConnectionRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="getConnection"></a>
# **getConnection**
> ConnectionRead getConnection(connectionIdRequestBody)

Get a connection

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connectionIdRequestBody** | [**ConnectionIdRequestBody**](../io.dataline.api.client.model/ConnectionIdRequestBody.md)|  |

### Return type

[**ConnectionRead**](../io.dataline.api.client.model/ConnectionRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="listConnectionsForWorkspace"></a>
# **listConnectionsForWorkspace**
> ConnectionReadList listConnectionsForWorkspace(workspaceIdRequestBody)

Returns all connections for a workspace.

    List connections for workspace. Does not return deleted connections.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspaceIdRequestBody** | [**WorkspaceIdRequestBody**](../io.dataline.api.client.model/WorkspaceIdRequestBody.md)|  |

### Return type

[**ConnectionReadList**](../io.dataline.api.client.model/ConnectionReadList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="syncConnection"></a>
# **syncConnection**
> ConnectionSyncRead syncConnection(connectionIdRequestBody)

Trigger a manual sync of the connection

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connectionIdRequestBody** | [**ConnectionIdRequestBody**](../io.dataline.api.client.model/ConnectionIdRequestBody.md)|  |

### Return type

[**ConnectionSyncRead**](../io.dataline.api.client.model/ConnectionSyncRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateConnection"></a>
# **updateConnection**
> ConnectionRead updateConnection(connectionUpdate)

Updated a connection status

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connectionUpdate** | [**ConnectionUpdate**](../io.dataline.api.client.model/ConnectionUpdate.md)|  |

### Return type

[**ConnectionRead**](../io.dataline.api.client.model/ConnectionRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


# WorkspaceApi

All URIs are relative to *https://virtserver.swaggerhub.com/cgardens6/dataline/1.0.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getWorkspace**](WorkspaceApi.md#getWorkspace) | **POST** /v1/workspaces/get | Find workspace by ID
[**getWorkspaceBySlug**](WorkspaceApi.md#getWorkspaceBySlug) | **POST** /v1/workspaces/get_by_slug | Find workspace by slug
[**updateWorkspace**](WorkspaceApi.md#updateWorkspace) | **POST** /v1/workspaces/update | Update workspace state


<a name="getWorkspace"></a>
# **getWorkspace**
> WorkspaceRead getWorkspace(workspaceIdRequestBody)

Find workspace by ID

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspaceIdRequestBody** | [**WorkspaceIdRequestBody**](../io.dataline.api.client.model/WorkspaceIdRequestBody.md)|  |

### Return type

[**WorkspaceRead**](../io.dataline.api.client.model/WorkspaceRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="getWorkspaceBySlug"></a>
# **getWorkspaceBySlug**
> WorkspaceRead getWorkspaceBySlug(slugRequestBody)

Find workspace by slug

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **slugRequestBody** | [**SlugRequestBody**](../io.dataline.api.client.model/SlugRequestBody.md)|  |

### Return type

[**WorkspaceRead**](../io.dataline.api.client.model/WorkspaceRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateWorkspace"></a>
# **updateWorkspace**
> WorkspaceRead updateWorkspace(workspaceUpdate)

Update workspace state

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspaceUpdate** | [**WorkspaceUpdate**](../io.dataline.api.client.model/WorkspaceUpdate.md)|  |

### Return type

[**WorkspaceRead**](../io.dataline.api.client.model/WorkspaceRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


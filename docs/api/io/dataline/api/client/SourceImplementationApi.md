# SourceImplementationApi

All URIs are relative to *https://virtserver.swaggerhub.com/cgardens6/dataline/1.0.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**checkConnectionToSourceImplementation**](SourceImplementationApi.md#checkConnectionToSourceImplementation) | **POST** /v1/source_implementations/check_connection | Check connection to the source implementation
[**createSourceImplementation**](SourceImplementationApi.md#createSourceImplementation) | **POST** /v1/source_implementations/create | Create a source implementation
[**deleteSourceImplementation**](SourceImplementationApi.md#deleteSourceImplementation) | **POST** /v1/source_implementations/delete | Delete a source implementation
[**discoverSchemaForSourceImplementation**](SourceImplementationApi.md#discoverSchemaForSourceImplementation) | **POST** /v1/source_implementations/discover_schema | Discover the schema of the source implementation
[**getSourceImplementation**](SourceImplementationApi.md#getSourceImplementation) | **POST** /v1/source_implementations/get | Get source implementation
[**listSourceImplementationsForWorkspace**](SourceImplementationApi.md#listSourceImplementationsForWorkspace) | **POST** /v1/source_implementations/list | List source implementations for workspace
[**updateSourceImplementation**](SourceImplementationApi.md#updateSourceImplementation) | **POST** /v1/source_implementations/update | Update a source


<a name="checkConnectionToSourceImplementation"></a>
# **checkConnectionToSourceImplementation**
> CheckConnectionRead checkConnectionToSourceImplementation(sourceImplementationIdRequestBody)

Check connection to the source implementation

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sourceImplementationIdRequestBody** | [**SourceImplementationIdRequestBody**](../io.dataline.api.client.model/SourceImplementationIdRequestBody.md)|  |

### Return type

[**CheckConnectionRead**](../io.dataline.api.client.model/CheckConnectionRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="createSourceImplementation"></a>
# **createSourceImplementation**
> SourceImplementationRead createSourceImplementation(sourceImplementationCreate)

Create a source implementation

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sourceImplementationCreate** | [**SourceImplementationCreate**](../io.dataline.api.client.model/SourceImplementationCreate.md)|  |

### Return type

[**SourceImplementationRead**](../io.dataline.api.client.model/SourceImplementationRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteSourceImplementation"></a>
# **deleteSourceImplementation**
> deleteSourceImplementation(sourceImplementationIdRequestBody)

Delete a source implementation

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sourceImplementationIdRequestBody** | [**SourceImplementationIdRequestBody**](../io.dataline.api.client.model/SourceImplementationIdRequestBody.md)|  |

### Return type

null (empty response body)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined

<a name="discoverSchemaForSourceImplementation"></a>
# **discoverSchemaForSourceImplementation**
> SourceImplementationDiscoverSchemaRead discoverSchemaForSourceImplementation(sourceImplementationIdRequestBody)

Discover the schema of the source implementation

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sourceImplementationIdRequestBody** | [**SourceImplementationIdRequestBody**](../io.dataline.api.client.model/SourceImplementationIdRequestBody.md)|  |

### Return type

[**SourceImplementationDiscoverSchemaRead**](../io.dataline.api.client.model/SourceImplementationDiscoverSchemaRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="getSourceImplementation"></a>
# **getSourceImplementation**
> SourceImplementationRead getSourceImplementation(sourceImplementationIdRequestBody)

Get source implementation

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sourceImplementationIdRequestBody** | [**SourceImplementationIdRequestBody**](../io.dataline.api.client.model/SourceImplementationIdRequestBody.md)|  |

### Return type

[**SourceImplementationRead**](../io.dataline.api.client.model/SourceImplementationRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="listSourceImplementationsForWorkspace"></a>
# **listSourceImplementationsForWorkspace**
> SourceImplementationReadList listSourceImplementationsForWorkspace(workspaceIdRequestBody)

List source implementations for workspace

    List source implementations for workspace. Does not return deleted source implementations.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspaceIdRequestBody** | [**WorkspaceIdRequestBody**](../io.dataline.api.client.model/WorkspaceIdRequestBody.md)|  |

### Return type

[**SourceImplementationReadList**](../io.dataline.api.client.model/SourceImplementationReadList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateSourceImplementation"></a>
# **updateSourceImplementation**
> SourceImplementationRead updateSourceImplementation(sourceImplementationUpdate)

Update a source

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sourceImplementationUpdate** | [**SourceImplementationUpdate**](../io.dataline.api.client.model/SourceImplementationUpdate.md)|  |

### Return type

[**SourceImplementationRead**](../io.dataline.api.client.model/SourceImplementationRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


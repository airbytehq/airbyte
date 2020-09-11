# DestinationImplementationApi

All URIs are relative to *https://virtserver.swaggerhub.com/cgardens6/dataline/1.0.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**checkConnectionToDestinationImplementation**](DestinationImplementationApi.md#checkConnectionToDestinationImplementation) | **POST** /v1/destination_implementations/check_connection | Check connection to the destination implementation
[**createDestinationImplementation**](DestinationImplementationApi.md#createDestinationImplementation) | **POST** /v1/destination_implementations/create | Create a destination implementation
[**getDestinationImplementation**](DestinationImplementationApi.md#getDestinationImplementation) | **POST** /v1/destination_implementations/get | get configured destination
[**listDestinationImplementationsForWorkspace**](DestinationImplementationApi.md#listDestinationImplementationsForWorkspace) | **POST** /v1/destination_implementations/list | List configured destinations for a workspace
[**updateDestinationImplementation**](DestinationImplementationApi.md#updateDestinationImplementation) | **POST** /v1/destination_implementations/update | Update a destination implementation


<a name="checkConnectionToDestinationImplementation"></a>
# **checkConnectionToDestinationImplementation**
> CheckConnectionRead checkConnectionToDestinationImplementation(destinationImplementationIdRequestBody)

Check connection to the destination implementation

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destinationImplementationIdRequestBody** | [**DestinationImplementationIdRequestBody**](../io.dataline.api.client.model/DestinationImplementationIdRequestBody.md)|  |

### Return type

[**CheckConnectionRead**](../io.dataline.api.client.model/CheckConnectionRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="createDestinationImplementation"></a>
# **createDestinationImplementation**
> DestinationImplementationRead createDestinationImplementation(destinationImplementationCreate)

Create a destination implementation

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destinationImplementationCreate** | [**DestinationImplementationCreate**](../io.dataline.api.client.model/DestinationImplementationCreate.md)|  |

### Return type

[**DestinationImplementationRead**](../io.dataline.api.client.model/DestinationImplementationRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="getDestinationImplementation"></a>
# **getDestinationImplementation**
> DestinationImplementationRead getDestinationImplementation(destinationImplementationIdRequestBody)

get configured destination

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destinationImplementationIdRequestBody** | [**DestinationImplementationIdRequestBody**](../io.dataline.api.client.model/DestinationImplementationIdRequestBody.md)|  |

### Return type

[**DestinationImplementationRead**](../io.dataline.api.client.model/DestinationImplementationRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="listDestinationImplementationsForWorkspace"></a>
# **listDestinationImplementationsForWorkspace**
> DestinationImplementationReadList listDestinationImplementationsForWorkspace(workspaceIdRequestBody)

List configured destinations for a workspace

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspaceIdRequestBody** | [**WorkspaceIdRequestBody**](../io.dataline.api.client.model/WorkspaceIdRequestBody.md)|  |

### Return type

[**DestinationImplementationReadList**](../io.dataline.api.client.model/DestinationImplementationReadList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateDestinationImplementation"></a>
# **updateDestinationImplementation**
> DestinationImplementationRead updateDestinationImplementation(destinationImplementationUpdate)

Update a destination implementation

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destinationImplementationUpdate** | [**DestinationImplementationUpdate**](../io.dataline.api.client.model/DestinationImplementationUpdate.md)|  |

### Return type

[**DestinationImplementationRead**](../io.dataline.api.client.model/DestinationImplementationRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


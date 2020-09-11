# DestinationApi

All URIs are relative to *https://virtserver.swaggerhub.com/cgardens6/dataline/1.0.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getDestination**](DestinationApi.md#getDestination) | **POST** /v1/destinations/get | Get destination
[**listDestinations**](DestinationApi.md#listDestinations) | **POST** /v1/destinations/list | List all of the destinations that Dataline supports


<a name="getDestination"></a>
# **getDestination**
> DestinationRead getDestination(destinationIdRequestBody)

Get destination

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destinationIdRequestBody** | [**DestinationIdRequestBody**](../io.dataline.api.client.model/DestinationIdRequestBody.md)|  |

### Return type

[**DestinationRead**](../io.dataline.api.client.model/DestinationRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="listDestinations"></a>
# **listDestinations**
> DestinationReadList listDestinations()

List all of the destinations that Dataline supports

### Parameters
This endpoint does not need any parameter.

### Return type

[**DestinationReadList**](../io.dataline.api.client.model/DestinationReadList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


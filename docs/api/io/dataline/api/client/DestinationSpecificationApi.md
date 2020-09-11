# DestinationSpecificationApi

All URIs are relative to *https://virtserver.swaggerhub.com/cgardens6/dataline/1.0.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getDestinationSpecification**](DestinationSpecificationApi.md#getDestinationSpecification) | **POST** /v1/destination_specifications/get | Get specification for a destination


<a name="getDestinationSpecification"></a>
# **getDestinationSpecification**
> DestinationSpecificationRead getDestinationSpecification(destinationIdRequestBody)

Get specification for a destination

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destinationIdRequestBody** | [**DestinationIdRequestBody**](../io.dataline.api.client.model/DestinationIdRequestBody.md)|  |

### Return type

[**DestinationSpecificationRead**](../io.dataline.api.client.model/DestinationSpecificationRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


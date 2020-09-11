# SourceSpecificationApi

All URIs are relative to *https://virtserver.swaggerhub.com/cgardens6/dataline/1.0.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getSourceSpecification**](SourceSpecificationApi.md#getSourceSpecification) | **POST** /v1/source_specifications/get | Get specification for a source.


<a name="getSourceSpecification"></a>
# **getSourceSpecification**
> SourceSpecificationRead getSourceSpecification(sourceIdRequestBody)

Get specification for a source.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sourceIdRequestBody** | [**SourceIdRequestBody**](../io.dataline.api.client.model/SourceIdRequestBody.md)|  |

### Return type

[**SourceSpecificationRead**](../io.dataline.api.client.model/SourceSpecificationRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


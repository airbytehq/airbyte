# SourceApi

All URIs are relative to *https://virtserver.swaggerhub.com/cgardens6/dataline/1.0.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getSource**](SourceApi.md#getSource) | **POST** /v1/sources/get | Get source
[**listSources**](SourceApi.md#listSources) | **POST** /v1/sources/list | List all of the sources that Dataline supports


<a name="getSource"></a>
# **getSource**
> SourceRead getSource(sourceIdRequestBody)

Get source

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sourceIdRequestBody** | [**SourceIdRequestBody**](../io.dataline.api.client.model/SourceIdRequestBody.md)|  |

### Return type

[**SourceRead**](../io.dataline.api.client.model/SourceRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="listSources"></a>
# **listSources**
> SourceReadList listSources()

List all of the sources that Dataline supports

### Parameters
This endpoint does not need any parameter.

### Return type

[**SourceReadList**](../io.dataline.api.client.model/SourceReadList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


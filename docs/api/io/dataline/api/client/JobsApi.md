# JobsApi

All URIs are relative to *https://virtserver.swaggerhub.com/cgardens6/dataline/1.0.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getJobInfo**](JobsApi.md#getJobInfo) | **POST** /v1/jobs/get | Get information about a job
[**listJobsFor**](JobsApi.md#listJobsFor) | **POST** /v1/jobs/list | Returns recent jobs for a connection. Jobs are returned in descending order by createdAt.


<a name="getJobInfo"></a>
# **getJobInfo**
> JobInfoRead getJobInfo(jobIdRequestBody)

Get information about a job

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jobIdRequestBody** | [**JobIdRequestBody**](../io.dataline.api.client.model/JobIdRequestBody.md)|  |

### Return type

[**JobInfoRead**](../io.dataline.api.client.model/JobInfoRead.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="listJobsFor"></a>
# **listJobsFor**
> JobReadList listJobsFor(jobListRequestBody)

Returns recent jobs for a connection. Jobs are returned in descending order by createdAt.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jobListRequestBody** | [**JobListRequestBody**](../io.dataline.api.client.model/JobListRequestBody.md)|  |

### Return type

[**JobReadList**](../io.dataline.api.client.model/JobReadList.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


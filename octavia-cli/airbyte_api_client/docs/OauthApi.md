# airbyte_api_client.OauthApi

All URIs are relative to *http://localhost:8000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**complete_destination_o_auth**](OauthApi.md#complete_destination_o_auth) | **POST** /v1/destination_oauths/complete_oauth | Given a destination def ID generate an access/refresh token etc.
[**complete_source_o_auth**](OauthApi.md#complete_source_o_auth) | **POST** /v1/source_oauths/complete_oauth | Given a source def ID generate an access/refresh token etc.
[**get_destination_o_auth_consent**](OauthApi.md#get_destination_o_auth_consent) | **POST** /v1/destination_oauths/get_consent_url | Given a destination connector definition ID, return the URL to the consent screen where to redirect the user to.
[**get_source_o_auth_consent**](OauthApi.md#get_source_o_auth_consent) | **POST** /v1/source_oauths/get_consent_url | Given a source connector definition ID, return the URL to the consent screen where to redirect the user to.
[**set_instancewide_destination_oauth_params**](OauthApi.md#set_instancewide_destination_oauth_params) | **POST** /v1/destination_oauths/oauth_params/create | Sets instancewide variables to be used for the oauth flow when creating this destination. When set, these variables will be injected into a connector&#39;s configuration before any interaction with the connector image itself. This enables running oauth flows with consistent variables e.g: the company&#39;s Google Ads developer_token, client_id, and client_secret without the user having to know about these variables. 
[**set_instancewide_source_oauth_params**](OauthApi.md#set_instancewide_source_oauth_params) | **POST** /v1/source_oauths/oauth_params/create | Sets instancewide variables to be used for the oauth flow when creating this source. When set, these variables will be injected into a connector&#39;s configuration before any interaction with the connector image itself. This enables running oauth flows with consistent variables e.g: the company&#39;s Google Ads developer_token, client_id, and client_secret without the user having to know about these variables. 


# **complete_destination_o_auth**
> CompleteOAuthResponse complete_destination_o_auth(complete_destination_o_auth_request)

Given a destination def ID generate an access/refresh token etc.

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import oauth_api
from airbyte_api_client.model.complete_destination_o_auth_request import CompleteDestinationOAuthRequest
from airbyte_api_client.model.complete_o_auth_response import CompleteOAuthResponse
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = oauth_api.OauthApi(api_client)
    complete_destination_o_auth_request = CompleteDestinationOAuthRequest(
        destination_definition_id="destination_definition_id_example",
        workspace_id="workspace_id_example",
        redirect_url="redirect_url_example",
        _query_params={},
        o_auth_input_configuration=None,
    ) # CompleteDestinationOAuthRequest | 

    # example passing only required values which don't have defaults set
    try:
        # Given a destination def ID generate an access/refresh token etc.
        api_response = api_instance.complete_destination_o_auth(complete_destination_o_auth_request)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling OauthApi->complete_destination_o_auth: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **complete_destination_o_auth_request** | [**CompleteDestinationOAuthRequest**](CompleteDestinationOAuthRequest.md)|  |

### Return type

[**CompleteOAuthResponse**](CompleteOAuthResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |
**404** | Object with given id was not found. |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **complete_source_o_auth**
> CompleteOAuthResponse complete_source_o_auth(complete_source_oauth_request)

Given a source def ID generate an access/refresh token etc.

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import oauth_api
from airbyte_api_client.model.complete_o_auth_response import CompleteOAuthResponse
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.complete_source_oauth_request import CompleteSourceOauthRequest
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = oauth_api.OauthApi(api_client)
    complete_source_oauth_request = CompleteSourceOauthRequest(
        source_definition_id="source_definition_id_example",
        workspace_id="workspace_id_example",
        redirect_url="redirect_url_example",
        _query_params={},
        o_auth_input_configuration=None,
    ) # CompleteSourceOauthRequest | 

    # example passing only required values which don't have defaults set
    try:
        # Given a source def ID generate an access/refresh token etc.
        api_response = api_instance.complete_source_o_auth(complete_source_oauth_request)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling OauthApi->complete_source_o_auth: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **complete_source_oauth_request** | [**CompleteSourceOauthRequest**](CompleteSourceOauthRequest.md)|  |

### Return type

[**CompleteOAuthResponse**](CompleteOAuthResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |
**404** | Object with given id was not found. |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_destination_o_auth_consent**
> OAuthConsentRead get_destination_o_auth_consent(destination_oauth_consent_request)

Given a destination connector definition ID, return the URL to the consent screen where to redirect the user to.

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import oauth_api
from airbyte_api_client.model.destination_oauth_consent_request import DestinationOauthConsentRequest
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.o_auth_consent_read import OAuthConsentRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = oauth_api.OauthApi(api_client)
    destination_oauth_consent_request = DestinationOauthConsentRequest(
        destination_definition_id="destination_definition_id_example",
        workspace_id="workspace_id_example",
        redirect_url="redirect_url_example",
        o_auth_input_configuration=None,
    ) # DestinationOauthConsentRequest | 

    # example passing only required values which don't have defaults set
    try:
        # Given a destination connector definition ID, return the URL to the consent screen where to redirect the user to.
        api_response = api_instance.get_destination_o_auth_consent(destination_oauth_consent_request)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling OauthApi->get_destination_o_auth_consent: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_oauth_consent_request** | [**DestinationOauthConsentRequest**](DestinationOauthConsentRequest.md)|  |

### Return type

[**OAuthConsentRead**](OAuthConsentRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |
**404** | Object with given id was not found. |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_source_o_auth_consent**
> OAuthConsentRead get_source_o_auth_consent(source_oauth_consent_request)

Given a source connector definition ID, return the URL to the consent screen where to redirect the user to.

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import oauth_api
from airbyte_api_client.model.source_oauth_consent_request import SourceOauthConsentRequest
from airbyte_api_client.model.invalid_input_exception_info import InvalidInputExceptionInfo
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.o_auth_consent_read import OAuthConsentRead
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = oauth_api.OauthApi(api_client)
    source_oauth_consent_request = SourceOauthConsentRequest(
        source_definition_id="source_definition_id_example",
        workspace_id="workspace_id_example",
        redirect_url="redirect_url_example",
        o_auth_input_configuration=None,
    ) # SourceOauthConsentRequest | 

    # example passing only required values which don't have defaults set
    try:
        # Given a source connector definition ID, return the URL to the consent screen where to redirect the user to.
        api_response = api_instance.get_source_o_auth_consent(source_oauth_consent_request)
        pprint(api_response)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling OauthApi->get_source_o_auth_consent: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_oauth_consent_request** | [**SourceOauthConsentRequest**](SourceOauthConsentRequest.md)|  |

### Return type

[**OAuthConsentRead**](OAuthConsentRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |
**404** | Object with given id was not found. |  -  |
**422** | Input failed validation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_instancewide_destination_oauth_params**
> set_instancewide_destination_oauth_params(set_instancewide_destination_oauth_params_request_body)

Sets instancewide variables to be used for the oauth flow when creating this destination. When set, these variables will be injected into a connector's configuration before any interaction with the connector image itself. This enables running oauth flows with consistent variables e.g: the company's Google Ads developer_token, client_id, and client_secret without the user having to know about these variables. 

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import oauth_api
from airbyte_api_client.model.set_instancewide_destination_oauth_params_request_body import SetInstancewideDestinationOauthParamsRequestBody
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.known_exception_info import KnownExceptionInfo
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = oauth_api.OauthApi(api_client)
    set_instancewide_destination_oauth_params_request_body = SetInstancewideDestinationOauthParamsRequestBody(
        destination_definition_id="destination_definition_id_example",
        params={},
    ) # SetInstancewideDestinationOauthParamsRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Sets instancewide variables to be used for the oauth flow when creating this destination. When set, these variables will be injected into a connector's configuration before any interaction with the connector image itself. This enables running oauth flows with consistent variables e.g: the company's Google Ads developer_token, client_id, and client_secret without the user having to know about these variables. 
        api_instance.set_instancewide_destination_oauth_params(set_instancewide_destination_oauth_params_request_body)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling OauthApi->set_instancewide_destination_oauth_params: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **set_instancewide_destination_oauth_params_request_body** | [**SetInstancewideDestinationOauthParamsRequestBody**](SetInstancewideDestinationOauthParamsRequestBody.md)|  |

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful |  -  |
**400** | Exception occurred; see message for details. |  -  |
**404** | Object with given id was not found. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_instancewide_source_oauth_params**
> set_instancewide_source_oauth_params(set_instancewide_source_oauth_params_request_body)

Sets instancewide variables to be used for the oauth flow when creating this source. When set, these variables will be injected into a connector's configuration before any interaction with the connector image itself. This enables running oauth flows with consistent variables e.g: the company's Google Ads developer_token, client_id, and client_secret without the user having to know about these variables. 

### Example


```python
import time
import airbyte_api_client
from airbyte_api_client.api import oauth_api
from airbyte_api_client.model.not_found_known_exception_info import NotFoundKnownExceptionInfo
from airbyte_api_client.model.known_exception_info import KnownExceptionInfo
from airbyte_api_client.model.set_instancewide_source_oauth_params_request_body import SetInstancewideSourceOauthParamsRequestBody
from pprint import pprint
# Defining the host is optional and defaults to http://localhost:8000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = airbyte_api_client.Configuration(
    host = "http://localhost:8000/api"
)


# Enter a context with an instance of the API client
with airbyte_api_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = oauth_api.OauthApi(api_client)
    set_instancewide_source_oauth_params_request_body = SetInstancewideSourceOauthParamsRequestBody(
        source_definition_id="source_definition_id_example",
        params={},
    ) # SetInstancewideSourceOauthParamsRequestBody | 

    # example passing only required values which don't have defaults set
    try:
        # Sets instancewide variables to be used for the oauth flow when creating this source. When set, these variables will be injected into a connector's configuration before any interaction with the connector image itself. This enables running oauth flows with consistent variables e.g: the company's Google Ads developer_token, client_id, and client_secret without the user having to know about these variables. 
        api_instance.set_instancewide_source_oauth_params(set_instancewide_source_oauth_params_request_body)
    except airbyte_api_client.ApiException as e:
        print("Exception when calling OauthApi->set_instancewide_source_oauth_params: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **set_instancewide_source_oauth_params_request_body** | [**SetInstancewideSourceOauthParamsRequestBody**](SetInstancewideSourceOauthParamsRequestBody.md)|  |

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful |  -  |
**400** | Exception occurred; see message for details. |  -  |
**404** | Object with given id was not found. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


# CompleteSourceOauthRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**source_definition_id** | **str** |  | 
**workspace_id** | **str** |  | 
**redirect_url** | **str** | When completing OAuth flow to gain an access token, some API sometimes requires to verify that the app re-send the redirectUrl that was used when consent was given. | [optional] 
**_query_params** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** | The query parameters present in the redirect URL after a user granted consent e.g auth code | [optional] 
**o_auth_input_configuration** | **bool, date, datetime, dict, float, int, list, str, none_type** | OAuth specific blob. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



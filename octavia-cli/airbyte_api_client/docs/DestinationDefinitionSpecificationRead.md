# DestinationDefinitionSpecificationRead


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**destination_definition_id** | **str** |  | 
**job_info** | [**SynchronousJobRead**](SynchronousJobRead.md) |  | 
**documentation_url** | **str** |  | [optional] 
**connection_specification** | **bool, date, datetime, dict, float, int, list, str, none_type** | The specification for what values are required to configure the destinationDefinition. | [optional] 
**auth_specification** | [**AuthSpecification**](AuthSpecification.md) |  | [optional] 
**advanced_auth** | [**AdvancedAuth**](AdvancedAuth.md) |  | [optional] 
**supported_destination_sync_modes** | [**[DestinationSyncMode]**](DestinationSyncMode.md) |  | [optional] 
**supports_dbt** | **bool** |  | [optional] 
**supports_normalization** | **bool** |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



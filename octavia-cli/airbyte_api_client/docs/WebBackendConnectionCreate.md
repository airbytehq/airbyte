# WebBackendConnectionCreate


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**source_id** | **str** |  | 
**destination_id** | **str** |  | 
**status** | [**ConnectionStatus**](ConnectionStatus.md) |  | 
**name** | **str** | Optional name of the connection | [optional] 
**namespace_definition** | [**NamespaceDefinitionType**](NamespaceDefinitionType.md) |  | [optional] 
**namespace_format** | **str** | Used when namespaceDefinition is &#39;customformat&#39;. If blank then behaves like namespaceDefinition &#x3D; &#39;destination&#39;. If \&quot;${SOURCE_NAMESPACE}\&quot; then behaves like namespaceDefinition &#x3D; &#39;source&#39;. | [optional]  if omitted the server will use the default value of "null"
**prefix** | **str** | Prefix that will be prepended to the name of each stream when it is written to the destination. | [optional] 
**operation_ids** | **[str]** |  | [optional] 
**sync_catalog** | [**AirbyteCatalog**](AirbyteCatalog.md) |  | [optional] 
**schedule** | [**ConnectionSchedule**](ConnectionSchedule.md) |  | [optional] 
**resource_requirements** | [**ResourceRequirements**](ResourceRequirements.md) |  | [optional] 
**operations** | [**[OperationCreate]**](OperationCreate.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



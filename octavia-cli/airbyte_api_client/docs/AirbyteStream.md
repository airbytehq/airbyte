# AirbyteStream

the immutable schema defined by the source

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Stream&#39;s name. | 
**json_schema** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** |  | [optional] 
**supported_sync_modes** | [**[SyncMode]**](SyncMode.md) |  | [optional] 
**source_defined_cursor** | **bool** | If the source defines the cursor field, then any other cursor field inputs will be ignored. If it does not, either the user_provided one is used, or the default one is used as a backup. | [optional] 
**default_cursor_field** | **[str]** | Path to the field that will be used to determine if a record is new or modified since the last sync. If not provided by the source, the end user will have to specify the comparable themselves. | [optional] 
**source_defined_primary_key** | **[[str]]** | If the source defines the primary key, paths to the fields that will be used as a primary key. If not provided by the source, the end user will have to specify the primary key themselves. | [optional] 
**namespace** | **str** | Optional Source-defined namespace. Airbyte streams from the same sources should have the same namespace. Currently only used by JDBC destinations to determine what schema to write to. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



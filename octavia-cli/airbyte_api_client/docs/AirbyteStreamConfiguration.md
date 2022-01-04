# AirbyteStreamConfiguration

the mutable part of the stream to configure the destination

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sync_mode** | [**SyncMode**](SyncMode.md) |  | 
**destination_sync_mode** | [**DestinationSyncMode**](DestinationSyncMode.md) |  | 
**cursor_field** | **[str]** | Path to the field that will be used to determine if a record is new or modified since the last sync. This field is REQUIRED if &#x60;sync_mode&#x60; is &#x60;incremental&#x60;. Otherwise it is ignored. | [optional] 
**primary_key** | **[[str]]** | Paths to the fields that will be used as primary key. This field is REQUIRED if &#x60;destination_sync_mode&#x60; is &#x60;*_dedup&#x60;. Otherwise it is ignored. | [optional] 
**alias_name** | **str** | Alias name to the stream to be used in the destination | [optional] 
**selected** | **bool** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



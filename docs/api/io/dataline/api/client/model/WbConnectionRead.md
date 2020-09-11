# WbConnectionRead
## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connectionId** | [**UUID**](UUID.md) |  | [default to null]
**name** | [**String**](string.md) |  | [default to null]
**sourceImplementationId** | [**UUID**](UUID.md) |  | [default to null]
**destinationImplementationId** | [**UUID**](UUID.md) |  | [default to null]
**syncMode** | [**String**](string.md) |  | [default to null]
**syncSchema** | [**SourceSchema**](SourceSchema.md) |  | [default to null]
**schedule** | [**ConnectionSchedule**](ConnectionSchedule.md) |  | [optional] [default to null]
**status** | [**ConnectionStatus**](ConnectionStatus.md) |  | [default to null]
**source** | [**SourceImplementationRead**](SourceImplementationRead.md) |  | [default to null]
**lastSync** | [**Long**](long.md) | epoch time of last sync. null if no sync has taken place. | [optional] [default to null]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


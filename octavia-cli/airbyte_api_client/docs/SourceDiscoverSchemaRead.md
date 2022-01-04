# SourceDiscoverSchemaRead

Returns the results of a discover catalog job. If the job was not successful, the catalog field will not be present. jobInfo will aways be present and its status be used to determine if the job was successful or not.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_info** | [**SynchronousJobRead**](SynchronousJobRead.md) |  | 
**catalog** | [**AirbyteCatalog**](AirbyteCatalog.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



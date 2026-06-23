---
id: airbyte_agent_sdk-connectors-snowflake-models
title: airbyte_agent_sdk.connectors.snowflake.models
---

Module airbyte_agent_sdk.connectors.snowflake.models
====================================================
Pydantic models for snowflake connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="ColumnsListResultMeta"></a>

`ColumnsListResultMeta(**data: Any)`
:   Metadata for columns.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

    `partition_info: list[airbyte_agent_sdk.connectors.snowflake.models.PartitionInfo] | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

<a id="ColumnsResponse"></a>

`ColumnsResponse(**data: Any)`
:   ColumnsResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `created_on: int | None`
    :   The type of the None singleton.

    `data: list[list[typing.Any]] | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `result_set_meta_data: airbyte_agent_sdk.connectors.snowflake.models.ResultSetMetaData | None`
    :   The type of the None singleton.

    `sql_state: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

    `statement_status_url: str | None`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.snowflake.models.ColumnsResponseStats | None`
    :   The type of the None singleton.

<a id="ColumnsResponseStats"></a>

`ColumnsResponseStats(**data: Any)`
:   DML statistics returned for INSERT, UPDATE, DELETE, and MERGE statements. Not present for SELECT or SHOW queries.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `num_dml_duplicates: int | None`
    :   Number of duplicate rows skipped

    `num_rows_deleted: int | None`
    :   Number of rows deleted

    `num_rows_inserted: int | None`
    :   Number of rows inserted

    `num_rows_updated: int | None`
    :   Number of rows updated

<a id="DatabasesListResultMeta"></a>

`DatabasesListResultMeta(**data: Any)`
:   Metadata for databases.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

    `partition_info: list[airbyte_agent_sdk.connectors.snowflake.models.PartitionInfo] | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

<a id="DatabasesResponse"></a>

`DatabasesResponse(**data: Any)`
:   DatabasesResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `created_on: int | None`
    :   The type of the None singleton.

    `data: list[list[typing.Any]] | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `result_set_meta_data: airbyte_agent_sdk.connectors.snowflake.models.ResultSetMetaData | None`
    :   The type of the None singleton.

    `sql_state: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

    `statement_status_url: str | None`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.snowflake.models.DatabasesResponseStats | None`
    :   The type of the None singleton.

<a id="DatabasesResponseStats"></a>

`DatabasesResponseStats(**data: Any)`
:   DML statistics returned for INSERT, UPDATE, DELETE, and MERGE statements. Not present for SELECT or SHOW queries.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `num_dml_duplicates: int | None`
    :   Number of duplicate rows skipped

    `num_rows_deleted: int | None`
    :   Number of rows deleted

    `num_rows_inserted: int | None`
    :   Number of rows inserted

    `num_rows_updated: int | None`
    :   Number of rows updated

<a id="PartitionInfo"></a>

`PartitionInfo(**data: Any)`
:   Information about a result partition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `compressed_size: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `row_count: int | None`
    :   The type of the None singleton.

    `uncompressed_size: int | None`
    :   The type of the None singleton.

<a id="RecordListResultMeta"></a>

`RecordListResultMeta(**data: Any)`
:   Metadata for record.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

    `partition_info: list[airbyte_agent_sdk.connectors.snowflake.models.PartitionInfo] | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

<a id="RecordResponse"></a>

`RecordResponse(**data: Any)`
:   RecordResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `created_on: int | None`
    :   The type of the None singleton.

    `data: list[list[typing.Any]] | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `result_set_meta_data: airbyte_agent_sdk.connectors.snowflake.models.ResultSetMetaData | None`
    :   The type of the None singleton.

    `sql_state: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

    `statement_status_url: str | None`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.snowflake.models.RecordResponseStats | None`
    :   The type of the None singleton.

<a id="RecordResponseStats"></a>

`RecordResponseStats(**data: Any)`
:   DML statistics returned for INSERT, UPDATE, DELETE, and MERGE statements. Not present for SELECT or SHOW queries.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `num_dml_duplicates: int | None`
    :   Number of duplicate rows skipped

    `num_rows_deleted: int | None`
    :   Number of rows deleted

    `num_rows_inserted: int | None`
    :   Number of rows inserted

    `num_rows_updated: int | None`
    :   Number of rows updated

<a id="ResultPartitionResponse"></a>

`ResultPartitionResponse(**data: Any)`
:   ResultPartitionResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `created_on: int | None`
    :   The type of the None singleton.

    `data: list[list[typing.Any]] | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `result_set_meta_data: airbyte_agent_sdk.connectors.snowflake.models.ResultSetMetaData | None`
    :   The type of the None singleton.

    `sql_state: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

    `statement_status_url: str | None`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.snowflake.models.ResultPartitionResponseStats | None`
    :   The type of the None singleton.

<a id="ResultPartitionResponseStats"></a>

`ResultPartitionResponseStats(**data: Any)`
:   DML statistics returned for INSERT, UPDATE, DELETE, and MERGE statements. Not present for SELECT or SHOW queries.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `num_dml_duplicates: int | None`
    :   Number of duplicate rows skipped

    `num_rows_deleted: int | None`
    :   Number of rows deleted

    `num_rows_inserted: int | None`
    :   Number of rows inserted

    `num_rows_updated: int | None`
    :   Number of rows updated

<a id="ResultSetMetaData"></a>

`ResultSetMetaData(**data: Any)`
:   Metadata about the result set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `format: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `num_rows: int | None`
    :   The type of the None singleton.

    `partition_info: list[airbyte_agent_sdk.connectors.snowflake.models.PartitionInfo] | None`
    :   The type of the None singleton.

    `row_type: list[airbyte_agent_sdk.connectors.snowflake.models.RowType] | None`
    :   The type of the None singleton.

<a id="RowType"></a>

`RowType(**data: Any)`
:   Column metadata describing a single column in the result set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `byte_length: typing.Any | None`
    :   The type of the None singleton.

    `collation: typing.Any | None`
    :   The type of the None singleton.

    `database: str | None`
    :   The type of the None singleton.

    `length: typing.Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `nullable: bool | None`
    :   The type of the None singleton.

    `precision: typing.Any | None`
    :   The type of the None singleton.

    `scale: typing.Any | None`
    :   The type of the None singleton.

    `schema_: str | None`
    :   The type of the None singleton.

    `table: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="SchemasListResultMeta"></a>

`SchemasListResultMeta(**data: Any)`
:   Metadata for schemas.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

    `partition_info: list[airbyte_agent_sdk.connectors.snowflake.models.PartitionInfo] | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

<a id="SchemasResponse"></a>

`SchemasResponse(**data: Any)`
:   SchemasResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `created_on: int | None`
    :   The type of the None singleton.

    `data: list[list[typing.Any]] | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `result_set_meta_data: airbyte_agent_sdk.connectors.snowflake.models.ResultSetMetaData | None`
    :   The type of the None singleton.

    `sql_state: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

    `statement_status_url: str | None`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.snowflake.models.SchemasResponseStats | None`
    :   The type of the None singleton.

<a id="SchemasResponseStats"></a>

`SchemasResponseStats(**data: Any)`
:   DML statistics returned for INSERT, UPDATE, DELETE, and MERGE statements. Not present for SELECT or SHOW queries.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `num_dml_duplicates: int | None`
    :   Number of duplicate rows skipped

    `num_rows_deleted: int | None`
    :   Number of rows deleted

    `num_rows_inserted: int | None`
    :   Number of rows inserted

    `num_rows_updated: int | None`
    :   Number of rows updated

<a id="SnowflakeAuthConfig"></a>

`SnowflakeAuthConfig(**data: Any)`
:   PAT Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `programmatic_access_token: str`
    :   Snowflake Programmatic Access Token (PAT) for authentication. Generate one via ALTER USER ADD PROGRAMMATIC ACCESS TOKEN in Snowflake.

<a id="SnowflakeCheckResult"></a>

`SnowflakeCheckResult(**data: Any)`
:   Result of a health check operation.
    
    Returned by the check() method to indicate connectivity and credential status.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checked_action: str | None`
    :   Action name used for the health check.

    `checked_entity: str | None`
    :   Entity name used for the health check.

    `error: str | None`
    :   Error message if status is 'unhealthy', None otherwise.

    `model_config`
    :   The type of the None singleton.

    `status: str`
    :   Health check status: 'healthy' or 'unhealthy'.

<a id="SnowflakeExecuteResult"></a>

`SnowflakeExecuteResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="SnowflakeExecuteResultWithMeta"></a>

`SnowflakeExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[ColumnsResponse, ColumnsListResultMeta]
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[DatabasesResponse, DatabasesListResultMeta]
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[RecordResponse, RecordListResultMeta]
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[SchemasResponse, SchemasListResultMeta]
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[TablesResponse, TablesListResultMeta]
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[ViewsResponse, ViewsListResultMeta]
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[WarehousesResponse, WarehousesListResultMeta]

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`SnowflakeExecuteResultWithMeta[ColumnsResponse, ColumnsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ColumnsListResult"></a>

`ColumnsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnowflakeExecuteResultWithMeta[DatabasesResponse, DatabasesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DatabasesListResult"></a>

`DatabasesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnowflakeExecuteResultWithMeta[RecordResponse, RecordListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RecordListResult"></a>

`RecordListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnowflakeExecuteResultWithMeta[SchemasResponse, SchemasListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SchemasListResult"></a>

`SchemasListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnowflakeExecuteResultWithMeta[TablesResponse, TablesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TablesListResult"></a>

`TablesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnowflakeExecuteResultWithMeta[ViewsResponse, ViewsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ViewsListResult"></a>

`ViewsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnowflakeExecuteResultWithMeta[WarehousesResponse, WarehousesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WarehousesListResult"></a>

`WarehousesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SnowflakeReplicationConfig"></a>

`SnowflakeReplicationConfig(**data: Any)`
:   Snowflake Connection Settings - Database, warehouse, and role settings required for connecting to Snowflake. These map to the corresponding Airbyte source-snowflake configuration fields.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `database: str`
    :   The database for Airbyte to access data.

    `model_config`
    :   The type of the None singleton.

    `role: str`
    :   The role for Airbyte to access Snowflake.

    `warehouse: str`
    :   The warehouse for Airbyte to access data.

<a id="StatementResponse"></a>

`StatementResponse(**data: Any)`
:   Response from the Snowflake SQL API containing result set metadata and data rows. Used by all SHOW statement operations.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `created_on: int | None`
    :   The type of the None singleton.

    `data: list[list[typing.Any]] | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `result_set_meta_data: airbyte_agent_sdk.connectors.snowflake.models.ResultSetMetaData | None`
    :   The type of the None singleton.

    `sql_state: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

    `statement_status_url: str | None`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.snowflake.models.StatementResponseStats | None`
    :   The type of the None singleton.

<a id="StatementResponseStats"></a>

`StatementResponseStats(**data: Any)`
:   DML statistics returned for INSERT, UPDATE, DELETE, and MERGE statements. Not present for SELECT or SHOW queries.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `num_dml_duplicates: int | None`
    :   Number of duplicate rows skipped

    `num_rows_deleted: int | None`
    :   Number of rows deleted

    `num_rows_inserted: int | None`
    :   Number of rows inserted

    `num_rows_updated: int | None`
    :   Number of rows updated

<a id="TablesListResultMeta"></a>

`TablesListResultMeta(**data: Any)`
:   Metadata for tables.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

    `partition_info: list[airbyte_agent_sdk.connectors.snowflake.models.PartitionInfo] | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

<a id="TablesResponse"></a>

`TablesResponse(**data: Any)`
:   TablesResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `created_on: int | None`
    :   The type of the None singleton.

    `data: list[list[typing.Any]] | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `result_set_meta_data: airbyte_agent_sdk.connectors.snowflake.models.ResultSetMetaData | None`
    :   The type of the None singleton.

    `sql_state: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

    `statement_status_url: str | None`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.snowflake.models.TablesResponseStats | None`
    :   The type of the None singleton.

<a id="TablesResponseStats"></a>

`TablesResponseStats(**data: Any)`
:   DML statistics returned for INSERT, UPDATE, DELETE, and MERGE statements. Not present for SELECT or SHOW queries.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `num_dml_duplicates: int | None`
    :   Number of duplicate rows skipped

    `num_rows_deleted: int | None`
    :   Number of rows deleted

    `num_rows_inserted: int | None`
    :   Number of rows inserted

    `num_rows_updated: int | None`
    :   Number of rows updated

<a id="ViewsListResultMeta"></a>

`ViewsListResultMeta(**data: Any)`
:   Metadata for views.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

    `partition_info: list[airbyte_agent_sdk.connectors.snowflake.models.PartitionInfo] | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

<a id="ViewsResponse"></a>

`ViewsResponse(**data: Any)`
:   ViewsResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `created_on: int | None`
    :   The type of the None singleton.

    `data: list[list[typing.Any]] | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `result_set_meta_data: airbyte_agent_sdk.connectors.snowflake.models.ResultSetMetaData | None`
    :   The type of the None singleton.

    `sql_state: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

    `statement_status_url: str | None`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.snowflake.models.ViewsResponseStats | None`
    :   The type of the None singleton.

<a id="ViewsResponseStats"></a>

`ViewsResponseStats(**data: Any)`
:   DML statistics returned for INSERT, UPDATE, DELETE, and MERGE statements. Not present for SELECT or SHOW queries.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `num_dml_duplicates: int | None`
    :   Number of duplicate rows skipped

    `num_rows_deleted: int | None`
    :   Number of rows deleted

    `num_rows_inserted: int | None`
    :   Number of rows inserted

    `num_rows_updated: int | None`
    :   Number of rows updated

<a id="WarehousesListResultMeta"></a>

`WarehousesListResultMeta(**data: Any)`
:   Metadata for warehouses.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

    `partition_info: list[airbyte_agent_sdk.connectors.snowflake.models.PartitionInfo] | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

<a id="WarehousesResponse"></a>

`WarehousesResponse(**data: Any)`
:   WarehousesResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `created_on: int | None`
    :   The type of the None singleton.

    `data: list[list[typing.Any]] | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `result_set_meta_data: airbyte_agent_sdk.connectors.snowflake.models.ResultSetMetaData | None`
    :   The type of the None singleton.

    `sql_state: str | None`
    :   The type of the None singleton.

    `statement_handle: str | None`
    :   The type of the None singleton.

    `statement_status_url: str | None`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.snowflake.models.WarehousesResponseStats | None`
    :   The type of the None singleton.

<a id="WarehousesResponseStats"></a>

`WarehousesResponseStats(**data: Any)`
:   DML statistics returned for INSERT, UPDATE, DELETE, and MERGE statements. Not present for SELECT or SHOW queries.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `num_dml_duplicates: int | None`
    :   Number of duplicate rows skipped

    `num_rows_deleted: int | None`
    :   Number of rows deleted

    `num_rows_inserted: int | None`
    :   Number of rows inserted

    `num_rows_updated: int | None`
    :   Number of rows updated
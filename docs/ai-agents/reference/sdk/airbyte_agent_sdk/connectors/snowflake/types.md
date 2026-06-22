---
id: airbyte_agent_sdk-connectors-snowflake-types
title: airbyte_agent_sdk.connectors.snowflake.types
---

Module airbyte_agent_sdk.connectors.snowflake.types
===================================================
Type definitions for snowflake connector.

Classes
-------

<a id="ColumnsListParams"></a>

`ColumnsListParams(*args, **kwargs)`
:   Parameters for columns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `database: str`
    :   The type of the None singleton.

    `parameters: dict[str, typing.Any]`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `schema: str`
    :   The type of the None singleton.

    `statement: str`
    :   The type of the None singleton.

    `timeout: int`
    :   The type of the None singleton.

    `warehouse: str`
    :   The type of the None singleton.

<a id="DatabasesListParams"></a>

`DatabasesListParams(*args, **kwargs)`
:   Parameters for databases.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `database: str`
    :   The type of the None singleton.

    `parameters: dict[str, typing.Any]`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `schema: str`
    :   The type of the None singleton.

    `statement: str`
    :   The type of the None singleton.

    `timeout: int`
    :   The type of the None singleton.

    `warehouse: str`
    :   The type of the None singleton.

<a id="RecordCreateParams"></a>

`RecordCreateParams(*args, **kwargs)`
:   Parameters for record.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `database: str`
    :   The type of the None singleton.

    `parameters: dict[str, typing.Any]`
    :   The type of the None singleton.

    `request_id: str`
    :   The type of the None singleton.

    `retry: bool`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `schema: str`
    :   The type of the None singleton.

    `statement: str`
    :   The type of the None singleton.

    `timeout: int`
    :   The type of the None singleton.

    `warehouse: str`
    :   The type of the None singleton.

<a id="RecordDeleteParams"></a>

`RecordDeleteParams(*args, **kwargs)`
:   Parameters for record.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `database: str`
    :   The type of the None singleton.

    `parameters: dict[str, typing.Any]`
    :   The type of the None singleton.

    `request_id: str`
    :   The type of the None singleton.

    `retry: bool`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `schema: str`
    :   The type of the None singleton.

    `statement: str`
    :   The type of the None singleton.

    `timeout: int`
    :   The type of the None singleton.

    `warehouse: str`
    :   The type of the None singleton.

<a id="RecordGetParams"></a>

`RecordGetParams(*args, **kwargs)`
:   Parameters for record.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `database: str`
    :   The type of the None singleton.

    `parameters: dict[str, typing.Any]`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `schema: str`
    :   The type of the None singleton.

    `statement: str`
    :   The type of the None singleton.

    `timeout: int`
    :   The type of the None singleton.

    `warehouse: str`
    :   The type of the None singleton.

<a id="RecordListParams"></a>

`RecordListParams(*args, **kwargs)`
:   Parameters for record.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `database: str`
    :   The type of the None singleton.

    `parameters: dict[str, typing.Any]`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `schema: str`
    :   The type of the None singleton.

    `statement: str`
    :   The type of the None singleton.

    `timeout: int`
    :   The type of the None singleton.

    `warehouse: str`
    :   The type of the None singleton.

<a id="RecordUpdateParams"></a>

`RecordUpdateParams(*args, **kwargs)`
:   Parameters for record.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `database: str`
    :   The type of the None singleton.

    `parameters: dict[str, typing.Any]`
    :   The type of the None singleton.

    `request_id: str`
    :   The type of the None singleton.

    `retry: bool`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `schema: str`
    :   The type of the None singleton.

    `statement: str`
    :   The type of the None singleton.

    `timeout: int`
    :   The type of the None singleton.

    `warehouse: str`
    :   The type of the None singleton.

<a id="ResultPartitionsGetParams"></a>

`ResultPartitionsGetParams(*args, **kwargs)`
:   Parameters for result_partitions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `partition: int`
    :   The type of the None singleton.

    `request_id: str`
    :   The type of the None singleton.

    `statement_handle: str`
    :   The type of the None singleton.

<a id="SchemasListParams"></a>

`SchemasListParams(*args, **kwargs)`
:   Parameters for schemas.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `database: str`
    :   The type of the None singleton.

    `parameters: dict[str, typing.Any]`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `schema: str`
    :   The type of the None singleton.

    `statement: str`
    :   The type of the None singleton.

    `timeout: int`
    :   The type of the None singleton.

    `warehouse: str`
    :   The type of the None singleton.

<a id="TablesListParams"></a>

`TablesListParams(*args, **kwargs)`
:   Parameters for tables.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `database: str`
    :   The type of the None singleton.

    `parameters: dict[str, typing.Any]`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `schema: str`
    :   The type of the None singleton.

    `statement: str`
    :   The type of the None singleton.

    `timeout: int`
    :   The type of the None singleton.

    `warehouse: str`
    :   The type of the None singleton.

<a id="ViewsListParams"></a>

`ViewsListParams(*args, **kwargs)`
:   Parameters for views.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `database: str`
    :   The type of the None singleton.

    `parameters: dict[str, typing.Any]`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `schema: str`
    :   The type of the None singleton.

    `statement: str`
    :   The type of the None singleton.

    `timeout: int`
    :   The type of the None singleton.

    `warehouse: str`
    :   The type of the None singleton.

<a id="WarehousesListParams"></a>

`WarehousesListParams(*args, **kwargs)`
:   Parameters for warehouses.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `database: str`
    :   The type of the None singleton.

    `parameters: dict[str, typing.Any]`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `schema: str`
    :   The type of the None singleton.

    `statement: str`
    :   The type of the None singleton.

    `timeout: int`
    :   The type of the None singleton.

    `warehouse: str`
    :   The type of the None singleton.
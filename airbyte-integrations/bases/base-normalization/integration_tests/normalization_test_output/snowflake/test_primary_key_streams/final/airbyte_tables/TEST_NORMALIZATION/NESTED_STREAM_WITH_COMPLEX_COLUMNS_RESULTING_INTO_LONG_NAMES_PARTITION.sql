

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION"  as
      (
with __dbt__CTE__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_AB1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID,
    get_path(parse_json(PARTITION), '"double_array_data"') as DOUBLE_ARRAY_DATA,
    get_path(parse_json(PARTITION), '"DATA"') as DATA,
    get_path(parse_json(PARTITION), '"column`_''with""_quotes"') as "column`_'with""_quotes",
    _AIRBYTE_EMITTED_AT
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES" as table_alias
where PARTITION is not null
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition
),  __dbt__CTE__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_AB2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID,
    DOUBLE_ARRAY_DATA,
    DATA,
    "column`_'with""_quotes",
    _AIRBYTE_EMITTED_AT
from __dbt__CTE__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_AB1
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition
),  __dbt__CTE__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_AB3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(
    
    coalesce(cast(_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID as 
    varchar
), '') || '-' || coalesce(cast(DOUBLE_ARRAY_DATA as 
    varchar
), '') || '-' || coalesce(cast(DATA as 
    varchar
), '') || '-' || coalesce(cast("column`_'with""_quotes" as 
    varchar
), '')

 as 
    varchar
)) as _AIRBYTE_PARTITION_HASHID,
    tmp.*
from __dbt__CTE__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_AB2 tmp
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition
)-- Final base SQL model
select
    _AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID,
    DOUBLE_ARRAY_DATA,
    DATA,
    "column`_'with""_quotes",
    _AIRBYTE_EMITTED_AT,
    _AIRBYTE_PARTITION_HASHID
from __dbt__CTE__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_AB3
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition from "AIRBYTE_DATABASE".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES"
      );
    
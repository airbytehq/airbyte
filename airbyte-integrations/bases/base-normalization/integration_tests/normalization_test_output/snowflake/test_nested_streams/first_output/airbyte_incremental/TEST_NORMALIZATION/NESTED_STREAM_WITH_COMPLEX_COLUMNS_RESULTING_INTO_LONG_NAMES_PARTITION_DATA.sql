

      create or replace  table "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA"  as
      (select * from(
            
with __dbt__cte__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION"

select
    _AIRBYTE_PARTITION_HASHID,
    to_varchar(get_path(parse_json(DATA.value), '"currency"')) as CURRENCY,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION" as table_alias
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
cross join table(flatten(DATA)) as DATA
where 1 = 1
and DATA is not null

),  __dbt__cte__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB1
select
    _AIRBYTE_PARTITION_HASHID,
    cast(CURRENCY as 
    varchar
) as CURRENCY,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from __dbt__cte__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB1
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
where 1 = 1

),  __dbt__cte__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB2
select
    md5(cast(coalesce(cast(_AIRBYTE_PARTITION_HASHID as 
    varchar
), '') || '-' || coalesce(cast(CURRENCY as 
    varchar
), '') as 
    varchar
)) as _AIRBYTE_DATA_HASHID,
    tmp.*
from __dbt__cte__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB2 tmp
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
where 1 = 1

)-- Final base SQL model
-- depends_on: __dbt__cte__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB3
select
    _AIRBYTE_PARTITION_HASHID,
    CURRENCY,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_DATA_HASHID
from __dbt__cte__NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB3
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION"
where 1 = 1

            ) order by (_AIRBYTE_EMITTED_AT)
      );
    alter table "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA" cluster by (_AIRBYTE_EMITTED_AT);
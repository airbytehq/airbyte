
      

  create  table
    "normalization_tests".test_normalization_iprwf."nested_stream_with_complex_columns_resulting_into_long_names_partition_data"
    
    
      compound sortkey(_airbyte_emitted_at)
    
  as (
    
with __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "normalization_tests".test_normalization_iprwf."nested_stream_with_complex_columns_resulting_into_long_names_partition"

    with joined as (
            select
                table_alias._airbyte_partition_hashid as _airbyte_hashid,
                _airbyte_nested_data
            from "normalization_tests".test_normalization_iprwf."nested_stream_with_complex_columns_resulting_into_long_names_partition" as table_alias, table_alias.data as _airbyte_nested_data
        )
select
    _airbyte_partition_hashid,
    case when _airbyte_nested_data."currency" != '' then _airbyte_nested_data."currency" end as currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from "normalization_tests".test_normalization_iprwf."nested_stream_with_complex_columns_resulting_into_long_names_partition" as table_alias
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
left join joined on _airbyte_partition_hashid = joined._airbyte_hashid
where 1 = 1
and data is not null

),  __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab1
select
    _airbyte_partition_hashid,
    cast(currency as text) as currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab1
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
where 1 = 1

),  __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab2
select
    md5(cast(coalesce(cast(_airbyte_partition_hashid as text), '') || '-' || coalesce(cast(currency as text), '') as text)) as _airbyte_data_hashid,
    tmp.*
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab2 tmp
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
where 1 = 1

)-- Final base SQL model
-- depends_on: __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab3
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at,
    _airbyte_data_hashid
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab3
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from "normalization_tests".test_normalization_iprwf."nested_stream_with_complex_columns_resulting_into_long_names_partition"
where 1 = 1

  );
  
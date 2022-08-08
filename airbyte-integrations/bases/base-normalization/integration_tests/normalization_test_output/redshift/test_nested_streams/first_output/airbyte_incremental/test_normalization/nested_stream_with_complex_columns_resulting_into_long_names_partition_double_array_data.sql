
      

  create  table
    "integrationtests".test_normalization_xjvlg."nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data"
    
    
      compound sortkey(_airbyte_emitted_at)
    
  as (
    
with __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "integrationtests".test_normalization_xjvlg."nested_stream_with_complex_columns_resulting_into_long_names_partition"

    with joined as (
            select
                table_alias._airbyte_partition_hashid as _airbyte_hashid,
                _airbyte_nested_data
            from "integrationtests".test_normalization_xjvlg."nested_stream_with_complex_columns_resulting_into_long_names_partition" as table_alias, table_alias.double_array_data as _airbyte_nested_data
        )
select
    _airbyte_partition_hashid,
    case when _airbyte_nested_data."id" != '' then _airbyte_nested_data."id" end as id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from "integrationtests".test_normalization_xjvlg."nested_stream_with_complex_columns_resulting_into_long_names_partition" as table_alias
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
left join joined on _airbyte_partition_hashid = joined._airbyte_hashid
where 1 = 1
and double_array_data is not null

),  __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab1
select
    _airbyte_partition_hashid,
    cast(id as text) as id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab1
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
where 1 = 1

),  __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab2
select
    md5(cast(coalesce(cast(_airbyte_partition_hashid as text), '') || '-' || coalesce(cast(id as text), '') as text)) as _airbyte_double_array_data_hashid,
    tmp.*
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab2 tmp
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
where 1 = 1

)-- Final base SQL model
-- depends_on: __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab3
select
    _airbyte_partition_hashid,
    id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at,
    _airbyte_double_array_data_hashid
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab3
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data from "integrationtests".test_normalization_xjvlg."nested_stream_with_complex_columns_resulting_into_long_names_partition"
where 1 = 1

  );
  
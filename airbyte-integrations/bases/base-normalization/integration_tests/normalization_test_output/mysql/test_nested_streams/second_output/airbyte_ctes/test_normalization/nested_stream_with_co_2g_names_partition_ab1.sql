
  create view _airbyte_test_normalization.`nested_stream_with_co_2g_names_partition_ab1__dbt_tmp` as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_nested_strea__nto_long_names_hashid,
    json_extract(`partition`, 
    '$."double_array_data"') as double_array_data,
    json_extract(`partition`, 
    '$."DATA"') as `DATA`,
    json_extract(`partition`, 
    '$."column___with__quotes"') as `column__'with"_quotes`,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from test_normalization.`nested_stream_with_co__lting_into_long_names` as table_alias
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1
and `partition` is not null
  );

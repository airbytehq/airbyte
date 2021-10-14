
  create view _airbyte_test_normalization_namespace.`simple_stream_with_na_1g_into_long_names_ab1__dbt_tmp` as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, 
    '$."id"') as id,
    json_value(_airbyte_data, 
    '$."date"') as `date`,
    _airbyte_emitted_at
from test_normalization_namespace._airbyte_raw_simple_s__lting_into_long_names as table_alias
-- simple_stream_with_na__lting_into_long_names
  );

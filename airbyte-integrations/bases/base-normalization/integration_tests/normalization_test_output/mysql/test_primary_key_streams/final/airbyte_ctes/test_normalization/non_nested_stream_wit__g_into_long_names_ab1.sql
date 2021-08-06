
  create view _airbyte_test_normalization.`non_nested_stream_wit__g_into_long_names_ab1__dbt_tmp` as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, 
    '$."id"') as id,
    json_value(_airbyte_data, 
    '$."date"') as `date`,
    _airbyte_emitted_at
from test_normalization._airbyte_raw_non_nest__lting_into_long_names
-- non_nested_stream_wit__lting_into_long_names
  );


  create view _airbyte_test_normalization.`conflict_stream_array_ab1__dbt_tmp` as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, 
    '$."id"') as id,
    json_extract(table_alias._airbyte_data, 
    '$."conflict_stream_array"') as conflict_stream_array,
    _airbyte_emitted_at
from test_normalization._airbyte_raw_conflict_stream_array as table_alias
-- conflict_stream_array
  );

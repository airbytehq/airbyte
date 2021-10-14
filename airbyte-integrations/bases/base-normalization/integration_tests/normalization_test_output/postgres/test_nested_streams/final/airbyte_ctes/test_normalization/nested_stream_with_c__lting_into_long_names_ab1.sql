
  create view "postgres"._airbyte_test_normalization."nested_stream_with_c__lting_into_long_names_ab1__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path_text(_airbyte_data, 'date') as "date",
    
        jsonb_extract_path(table_alias._airbyte_data, 'partition')
     as "partition",
    _airbyte_emitted_at
from "postgres".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names as table_alias
-- nested_stream_with_c__lting_into_long_names
  );

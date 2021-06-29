
  create view "postgres"._airbyte_test_normalization."non_nested_stream_wi__lting_into_long_names_ab1__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path_text(_airbyte_data, 'date') as "date",
    _airbyte_emitted_at
from "postgres".test_normalization._airbyte_raw_non_nested_stream_without_namespace_resulting_into_long_names
-- non_nested_stream_wi__lting_into_long_names
  );

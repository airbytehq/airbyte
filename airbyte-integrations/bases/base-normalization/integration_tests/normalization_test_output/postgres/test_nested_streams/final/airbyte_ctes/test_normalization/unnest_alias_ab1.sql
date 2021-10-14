
  create view "postgres"._airbyte_test_normalization."unnest_alias_ab1__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path(_airbyte_data, 'children') as children,
    _airbyte_emitted_at
from "postgres".test_normalization._airbyte_raw_unnest_alias as table_alias
-- unnest_alias
  );

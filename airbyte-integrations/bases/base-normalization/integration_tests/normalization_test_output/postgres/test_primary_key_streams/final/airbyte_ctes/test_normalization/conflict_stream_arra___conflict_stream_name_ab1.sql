
  create view "postgres"._airbyte_test_normalization."conflict_stream_arra___conflict_stream_name_ab1__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_conflict_stream_array_2_hashid,
    jsonb_extract_path_text(_airbyte_nested_data, 'id') as "id",
    _airbyte_emitted_at
from "postgres".test_normalization."conflict_stream_array_conflict_stream_array" as table_alias
cross join jsonb_array_elements(
        case jsonb_typeof(conflict_stream_name)
        when 'array' then conflict_stream_name
        else '[]' end
    ) as _airbyte_nested_data
where conflict_stream_name is not null
-- conflict_stream_name at conflict_stream_array/conflict_stream_array/conflict_stream_name
  );

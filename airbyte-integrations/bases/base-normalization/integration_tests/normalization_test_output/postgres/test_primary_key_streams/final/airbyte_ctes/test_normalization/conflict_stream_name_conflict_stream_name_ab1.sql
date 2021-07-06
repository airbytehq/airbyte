
  create view "postgres"._airbyte_test_normalization."conflict_stream_name_conflict_stream_name_ab1__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_conflict_stream_name_hashid,
    jsonb_extract_path_text(_airbyte_nested_data, 'group') as "group",
    jsonb_extract_path(_airbyte_nested_data, 'description') as description,
    _airbyte_emitted_at
from "postgres".test_normalization."conflict_stream_name"
cross join jsonb_array_elements(
        case jsonb_typeof(conflict_stream_name)
        when 'array' then conflict_stream_name
        else '[]' end
    ) as _airbyte_nested_data
where conflict_stream_name is not null
-- conflict_stream_name at conflict_stream_name/conflict_stream_name
  );

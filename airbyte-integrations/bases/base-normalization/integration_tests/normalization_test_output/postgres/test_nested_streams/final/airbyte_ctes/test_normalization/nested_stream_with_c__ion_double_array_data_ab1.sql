
  create view "postgres"._airbyte_test_normalization."nested_stream_with_c__ion_double_array_data_ab1__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_partition_hashid,
    jsonb_extract_path_text(_airbyte_nested_data, 'id') as "id",
    _airbyte_emitted_at
from "postgres".test_normalization."nested_stream_with_c___long_names_partition" as table_alias
cross join jsonb_array_elements(
        case jsonb_typeof(double_array_data)
        when 'array' then double_array_data
        else '[]' end
    ) as _airbyte_nested_data
where double_array_data is not null
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
  );

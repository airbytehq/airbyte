{{ config(schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnest_cte('nested_stream_with_c___long_names_partition', 'partition', 'double_array_data') }}
select
    _airbyte_partition_hashid,
    {{ json_extract_scalar(unnested_column_value('double_array_data'), ['id'], ['id']) }} as {{ adapter.quote('id') }},
    _airbyte_emitted_at
from {{ ref('nested_stream_with_c___long_names_partition') }} as table_alias
{{ cross_join_unnest('partition', 'double_array_data') }}
where double_array_data is not null
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data


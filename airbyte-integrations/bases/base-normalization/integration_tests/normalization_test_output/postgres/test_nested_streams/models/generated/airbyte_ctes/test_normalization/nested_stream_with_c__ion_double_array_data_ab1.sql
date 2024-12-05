{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ ref('nested_stream_with_c___long_names_partition') }}
{{ unnest_cte(ref('nested_stream_with_c___long_names_partition'), 'partition', 'double_array_data') }}
select
    _airbyte_partition_hashid,
    {{ json_extract_scalar(unnested_column_value('double_array_data'), ['id'], ['id']) }} as {{ adapter.quote('id') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('nested_stream_with_c___long_names_partition') }} as table_alias
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
{{ cross_join_unnest('partition', 'double_array_data') }}
where 1 = 1
and double_array_data is not null
{{ incremental_clause('_airbyte_emitted_at', this) }}


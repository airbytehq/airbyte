{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION') }}
{{ unnest_cte(ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION'), 'PARTITION', 'DOUBLE_ARRAY_DATA') }}
select
    _AIRBYTE_PARTITION_HASHID,
    {{ json_extract_scalar(unnested_column_value('DOUBLE_ARRAY_DATA'), ['id'], ['id']) }} as ID,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION') }} as table_alias
-- DOUBLE_ARRAY_DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
{{ cross_join_unnest('PARTITION', 'DOUBLE_ARRAY_DATA') }}
where 1 = 1
and DOUBLE_ARRAY_DATA is not null
{{ incremental_clause('_AIRBYTE_EMITTED_AT', this) }}


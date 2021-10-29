{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnest_cte('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION', 'PARTITION', adapter.quote('column`_\'with""_quotes')) }}
select
    _AIRBYTE_PARTITION_HASHID,
    {{ json_extract_scalar(unnested_column_value(adapter.quote('column`_\'with""_quotes')), ['currency'], ['currency']) }} as CURRENCY,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION') }} as table_alias
-- COLUMN___WITH__QUOTES at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
{{ cross_join_unnest('PARTITION', adapter.quote('column`_\'with""_quotes')) }}
where 1 = 1
and {{ adapter.quote('column`_\'with""_quotes') }} is not null


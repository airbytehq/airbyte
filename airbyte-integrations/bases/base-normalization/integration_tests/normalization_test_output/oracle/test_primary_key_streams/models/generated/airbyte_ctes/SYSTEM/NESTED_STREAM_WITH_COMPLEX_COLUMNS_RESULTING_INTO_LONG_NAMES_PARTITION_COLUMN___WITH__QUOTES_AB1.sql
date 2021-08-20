{{ config(schema="SYSTEM", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnest_cte('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION', 'PARTITION', 'COLUMN___WITH__QUOTES') }}
select
    AIRBYTE_PARTITION_HASHID,
    {{ json_extract_scalar(unnested_column_value('COLUMN___WITH__QUOTES'), ['currency']) }} as CURRENCY,
    airbyte_emitted_at
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION') }}
{{ cross_join_unnest('PARTITION', 'COLUMN___WITH__QUOTES') }}
where COLUMN___WITH__QUOTES is not null
-- COLUMN___WITH__QUOTES at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes


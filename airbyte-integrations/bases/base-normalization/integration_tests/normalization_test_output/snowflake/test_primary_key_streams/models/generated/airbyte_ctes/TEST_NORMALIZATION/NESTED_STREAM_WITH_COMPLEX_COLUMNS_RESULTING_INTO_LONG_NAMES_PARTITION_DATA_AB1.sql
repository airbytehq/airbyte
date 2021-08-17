{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnest_cte('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION', 'PARTITION', 'DATA') }}
select
    _AIRBYTE_PARTITION_HASHID,
    {{ json_extract_scalar(unnested_column_value('DATA'), ['currency'], ['currency']) }} as CURRENCY,
    _airbyte_emitted_at
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION') }} as table_alias
{{ cross_join_unnest('PARTITION', 'DATA') }}
where DATA is not null
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA


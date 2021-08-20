{{ config(schema="SYSTEM", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnest_cte('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION', 'PARTITION', 'DATA') }}
select
    AIRBYTE_PARTITION_HASHID,
    {{ json_extract_scalar(unnested_column_value('DATA'), ['currency']) }} as CURRENCY,
    airbyte_emitted_at
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION') }}
{{ cross_join_unnest('PARTITION', 'DATA') }}
where DATA is not null
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA


{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnest_cte('nested_stream_with_complex_columns_resulting_into_long_names_partition', 'partition', 'data') }}
select
    {{ quote('_AIRBYTE_PARTITION_HASHID') }},
    {{ json_extract_scalar(unnested_column_value('data'), ['currency'], ['currency']) }} as currency,
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition') }} 
{{ cross_join_unnest('partition', 'data') }}
where data is not null
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA


{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by {{ quote('_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID') }}
    order by {{ quote('_AIRBYTE_EMITTED_AT') }} asc
  ) as {{ quote('_AIRBYTE_ROW_NUM') }},
  tmp.*
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_ab3') }} tmp
-- nested_stream_with_complex_columns_resulting_into_long_names from {{ source('test_normalization', 'airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names') }}


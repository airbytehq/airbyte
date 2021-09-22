{{ config(schema="test_normalization", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    {{ quote('DATE') }},
    partition,
  {{ quote('DATE') }} as {{ quote('_AIRBYTE_START_AT') }},
  lag({{ quote('DATE') }}) over (
    partition by id
    order by {{ quote('DATE') }} asc nulls first, {{ quote('DATE') }} desc, {{ quote('_AIRBYTE_EMITTED_AT') }} desc
  ) as {{ quote('_AIRBYTE_END_AT') }},
  case when lag({{ quote('DATE') }}) over (
    partition by id
    order by {{ quote('DATE') }} asc nulls first, {{ quote('DATE') }} desc, {{ quote('_AIRBYTE_EMITTED_AT') }} desc
  ) is null  then 1 else 0 end as {{ quote('_AIRBYTE_ACTIVE_ROW') }},
  {{ quote('_AIRBYTE_EMITTED_AT') }},
  {{ quote('_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_ab4') }}
-- nested_stream_with_complex_columns_resulting_into_long_names from {{ source('test_normalization', 'airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names') }}
where "_AIRBYTE_ROW_NUM" = 1


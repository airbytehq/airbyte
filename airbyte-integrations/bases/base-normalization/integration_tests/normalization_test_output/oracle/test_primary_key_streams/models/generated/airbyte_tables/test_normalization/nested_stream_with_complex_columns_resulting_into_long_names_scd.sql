{{ config(schema="test_normalization", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    {{ QUOTE('DATE') }},
    partition,
    {{ QUOTE('DATE') }} as airbyte_start_at,
    lag({{ QUOTE('DATE') }}) over (
        partition by id
        order by {{ QUOTE('DATE') }} desc, airbyte_emitted_at desc
    ) as airbyte_end_at,
    coalesce(cast(lag({{ QUOTE('DATE') }}) over (
        partition by id
        order by {{ QUOTE('DATE') }} desc, airbyte_emitted_at desc
    ) as varchar(200)), 'Latest') as airbyte_active_row,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_ab4') }}
-- nested_stream_with_complex_columns_resulting_into_long_names from {{ source('test_normalization', 'airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names') }}
where airbyte_row_num = 1


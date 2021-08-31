{{ config(schema="test_normalization", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    {{ quote('DATE') }},
    partition,
    {{ quote('DATE') }} as "_AIRBYTE_START_AT",
    lag({{ quote('DATE') }}) over (
        partition by id
        order by {{ quote('DATE') }} desc, {{ quote('_AIRBYTE_EMITTED_AT') }} desc
    ) as "_AIRBYTE_END_AT", 
    coalesce(cast(lag({{ quote('DATE') }}) over (
        partition by id
        order by {{ quote('DATE') }} desc, {{ quote('_AIRBYTE_EMITTED_AT') }} desc
    ) as varchar(200)), 'Latest') as "_AIRBYTE_ACTIVE_ROW",
    "_AIRBYTE_EMITTED_AT",
    {{ quote('_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_ab4') }}
-- nested_stream_with_complex_columns_resulting_into_long_names from {{ source('test_normalization', 'airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names') }}
where "_AIRBYTE_ROW_NUM" = 1


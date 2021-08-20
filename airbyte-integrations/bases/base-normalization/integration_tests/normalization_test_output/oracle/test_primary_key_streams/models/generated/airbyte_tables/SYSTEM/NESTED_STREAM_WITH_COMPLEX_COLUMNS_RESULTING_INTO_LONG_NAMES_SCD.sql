{{ config(schema="SYSTEM", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    ID,
    {{ QUOTE('DATE') }},
    PARTITION,
    {{ QUOTE('DATE') }} as airbyte_start_at,
    lag({{ QUOTE('DATE') }}) over (
        partition by ID
        order by {{ QUOTE('DATE') }} desc, airbyte_emitted_at desc
    ) as airbyte_end_at,
    coalesce(cast(lag({{ QUOTE('DATE') }}) over (
        partition by ID
        order by {{ QUOTE('DATE') }} desc, airbyte_emitted_at desc
    ) as varchar(200)), 'Latest') as airbyte_active_row,
    airbyte_emitted_at,
    AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_AB4') }}
-- NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES from {{ source('SYSTEM', 'AIRBYTE_RAW_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES') }}
where airbyte_row_num = 1


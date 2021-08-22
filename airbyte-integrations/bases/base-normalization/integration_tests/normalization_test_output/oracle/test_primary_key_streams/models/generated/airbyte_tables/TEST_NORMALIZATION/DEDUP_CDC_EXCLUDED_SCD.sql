{{ config(schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    ID,
    NAME,
    {{ QUOTE('_AB_CDC_LSN') }},
    {{ QUOTE('_AB_CDC_UPDATED_AT') }},
    {{ QUOTE('_AB_CDC_DELETED_AT') }},
    airbyte_emitted_at as airbyte_start_at,
    lag(airbyte_emitted_at) over (
        partition by ID
        order by airbyte_emitted_at desc, airbyte_emitted_at desc
    ) as airbyte_end_at,
    coalesce(cast(lag(airbyte_emitted_at) over (
        partition by ID
        order by airbyte_emitted_at desc, airbyte_emitted_at desc
    ) as varchar(200)), 'Latest') as airbyte_active_row,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID') }}
from {{ ref('DEDUP_CDC_EXCLUDED_AB4') }}
-- DEDUP_CDC_EXCLUDED from {{ source('TEST_NORMALIZATION', 'AIRBYTE_RAW_DEDUP_CDC_EXCLUDED') }}
where airbyte_row_num = 1


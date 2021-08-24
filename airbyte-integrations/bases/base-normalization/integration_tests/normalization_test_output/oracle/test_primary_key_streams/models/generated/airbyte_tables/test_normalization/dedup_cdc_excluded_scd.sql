{{ config(schema="test_normalization", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    name,
    {{ QUOTE('_AB_CDC_LSN') }},
    {{ QUOTE('_AB_CDC_UPDATED_AT') }},
    {{ QUOTE('_AB_CDC_DELETED_AT') }},
    airbyte_emitted_at as airbyte_start_at,
    lag(airbyte_emitted_at) over (
        partition by id
        order by airbyte_emitted_at desc, airbyte_emitted_at desc
    ) as airbyte_end_at,
    coalesce(cast(lag(airbyte_emitted_at) over (
        partition by id
        order by airbyte_emitted_at desc, airbyte_emitted_at desc
    ) as varchar(200)), 'Latest') as airbyte_active_row,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID') }}
from {{ ref('dedup_cdc_excluded_ab4') }}
-- dedup_cdc_excluded from {{ source('test_normalization', 'airbyte_raw_dedup_cdc_excluded') }}
where airbyte_row_num = 1


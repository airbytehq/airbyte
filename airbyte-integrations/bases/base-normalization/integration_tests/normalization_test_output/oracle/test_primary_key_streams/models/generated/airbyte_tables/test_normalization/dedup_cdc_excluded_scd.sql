{{ config(schema="test_normalization", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    name,
    {{ quote('_AB_CDC_LSN') }},
    {{ quote('_AB_CDC_UPDATED_AT') }},
    {{ quote('_AB_CDC_DELETED_AT') }},
  {{ quote('_AIRBYTE_EMITTED_AT') }} as {{ quote('_AIRBYTE_START_AT') }},
  lag({{ quote('_AIRBYTE_EMITTED_AT') }}) over (
    partition by id
    order by {{ quote('_AIRBYTE_EMITTED_AT') }} asc nulls first, {{ quote('_AIRBYTE_EMITTED_AT') }} desc, {{ quote('_AIRBYTE_EMITTED_AT') }} desc
  ) as {{ quote('_AIRBYTE_END_AT') }},
  case when lag({{ quote('_AIRBYTE_EMITTED_AT') }}) over (
    partition by id
    order by {{ quote('_AIRBYTE_EMITTED_AT') }} asc nulls first, {{ quote('_AIRBYTE_EMITTED_AT') }} desc, {{ quote('_AIRBYTE_EMITTED_AT') }} desc, {{ quote('_AB_CDC_UPDATED_AT') }} desc
  ) is null and {{ quote('_AB_CDC_DELETED_AT') }} is null  then 1 else 0 end as {{ quote('_AIRBYTE_ACTIVE_ROW') }},
  {{ quote('_AIRBYTE_EMITTED_AT') }},
  {{ quote('_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID') }}
from {{ ref('dedup_cdc_excluded_ab4') }}
-- dedup_cdc_excluded from {{ source('test_normalization', 'airbyte_raw_dedup_cdc_excluded') }}
where "_AIRBYTE_ROW_NUM" = 1


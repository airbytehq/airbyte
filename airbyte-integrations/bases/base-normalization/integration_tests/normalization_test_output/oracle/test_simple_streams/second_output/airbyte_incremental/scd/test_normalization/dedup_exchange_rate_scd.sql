

  create  table test_normalization.dedup_exchange_rate_scd__dbt_tmp
  
  as
    
-- depends_on: ref('dedup_exchange_rate_stg')
with

input_data as (
    select *
    from test_normalization.dedup_exchange_rate_stg
    -- dedup_exchange_rate from test_normalization.airbyte_raw_dedup_exchange_rate
),

scd_data as (
    -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
    select
      ora_hash(
            
                id || '~' ||
            
            
                currency || '~' ||
            
            
                nzd
            
    ) as "_AIRBYTE_UNIQUE_KEY",
      id,
      currency,
      "DATE",
      timestamp_col,
      hkd_special___characters,
      hkd_special___characters_1,
      nzd,
      usd,
      "DATE" as "_AIRBYTE_START_AT",
      lag("DATE") over (
        partition by id, currency, cast(nzd as varchar2(4000))
        order by
            "DATE" desc nulls last,
            "_AIRBYTE_EMITTED_AT" desc
      ) as "_AIRBYTE_END_AT",
      case when row_number() over (
        partition by id, currency, cast(nzd as varchar2(4000))
        order by
            "DATE" desc nulls last,
            "_AIRBYTE_EMITTED_AT" desc
      ) = 1 then 1 else 0 end as "_AIRBYTE_ACTIVE_ROW",
      "_AIRBYTE_AB_ID",
      "_AIRBYTE_EMITTED_AT",
      "_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID"
    from input_data
),
dedup_data as (
    select
        -- we need to ensure de-duplicated rows for merge/update queries
        -- additionally, we generate a unique key for the scd table
        row_number() over (
            partition by
                "_AIRBYTE_UNIQUE_KEY",
                "_AIRBYTE_START_AT",
                "_AIRBYTE_EMITTED_AT"
            order by "_AIRBYTE_ACTIVE_ROW" desc, "_AIRBYTE_AB_ID"
        ) as "_AIRBYTE_ROW_NUM",
        ora_hash(
            
                "_AIRBYTE_UNIQUE_KEY" || '~' ||
            
            
                "_AIRBYTE_START_AT" || '~' ||
            
            
                "_AIRBYTE_EMITTED_AT"
            
    ) as "_AIRBYTE_UNIQUE_KEY_SCD",
        scd_data.*
    from scd_data
)
select
    "_AIRBYTE_UNIQUE_KEY",
    "_AIRBYTE_UNIQUE_KEY_SCD",
    id,
    currency,
    "DATE",
    timestamp_col,
    hkd_special___characters,
    hkd_special___characters_1,
    nzd,
    usd,
    "_AIRBYTE_START_AT",
    "_AIRBYTE_END_AT",
    "_AIRBYTE_ACTIVE_ROW",
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT",
    "_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID"
from dedup_data where "_AIRBYTE_ROW_NUM" = 1
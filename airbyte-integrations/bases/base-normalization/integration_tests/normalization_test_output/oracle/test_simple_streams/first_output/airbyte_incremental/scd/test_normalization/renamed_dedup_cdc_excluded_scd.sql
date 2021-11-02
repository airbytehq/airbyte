

  create  table test_normalization.renamed_dedup_cdc_excluded_scd__dbt_tmp
  
  as
    
with

input_data as (
    select *
    from test_normalization.renamed_dedup_cdc_excluded_ab3
    -- renamed_dedup_cdc_excluded from test_normalization.airbyte_raw_renamed_dedup_cdc_excluded
),

scd_data as (
    -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
    select
      ora_hash(
            
                id
            
    ) as "_AIRBYTE_UNIQUE_KEY",
        id,
      "_AIRBYTE_EMITTED_AT" as "_AIRBYTE_START_AT",
      lag("_AIRBYTE_EMITTED_AT") over (
        partition by id
        order by
            "_AIRBYTE_EMITTED_AT" asc nulls last,
            "_AIRBYTE_EMITTED_AT" desc,
            "_AIRBYTE_EMITTED_AT" desc
      ) as "_AIRBYTE_END_AT",
      case when lag("_AIRBYTE_EMITTED_AT") over (
        partition by id
        order by
            "_AIRBYTE_EMITTED_AT" asc nulls last,
            "_AIRBYTE_EMITTED_AT" desc,
            "_AIRBYTE_EMITTED_AT" desc
      ) is null  then 1 else 0 end as "_AIRBYTE_ACTIVE_ROW",
      "_AIRBYTE_AB_ID",
      "_AIRBYTE_EMITTED_AT",
      "_AIRBYTE_RENAMED_DEDUP_CDC_EXCLUDED_HASHID"
    from input_data
),
dedup_data as (
    select
        -- we need to ensure de-duplicated rows for merge/update queries
        -- additionally, we generate a unique key for the scd table
        row_number() over (
            partition by "_AIRBYTE_UNIQUE_KEY", "_AIRBYTE_START_AT", "_AIRBYTE_EMITTED_AT"
            order by "_AIRBYTE_AB_ID"
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
    "_AIRBYTE_START_AT",
    "_AIRBYTE_END_AT",
    "_AIRBYTE_ACTIVE_ROW",
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT",
    "_AIRBYTE_RENAMED_DEDUP_CDC_EXCLUDED_HASHID"
from dedup_data where "_AIRBYTE_ROW_NUM" = 1
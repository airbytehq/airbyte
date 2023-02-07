
        
  
    
    
        
        insert into test_normalization.dedup_exchange_rate_scd ("_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "currency", "date", "timestamp_col", "HKD@spéçiäl & characters", "HKD_special___characters", "NZD", "USD", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_dedup_exchange_rate_hashid")
  
-- depends_on: ref('dedup_exchange_rate_stg')
with

input_data as (
    select *
    from _airbyte_test_normalization.dedup_exchange_rate_stg
    -- dedup_exchange_rate from test_normalization._airbyte_raw_dedup_exchange_rate
),

input_data_with_active_row_num as (
    select *,
      row_number() over (
        partition by id, currency, cast(NZD as String)
        order by
            date is null asc,
            date desc,
            _airbyte_emitted_at desc
      ) as _airbyte_active_row_num
    from input_data
),
scd_data as (
    -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
    select
      assumeNotNull(hex(MD5(
            
                toString(id) || '~' ||
            
            
                toString(currency) || '~' ||
            
            
                toString(NZD)
            
    ))) as _airbyte_unique_key,
      id,
      currency,
      date,
      timestamp_col,
      "HKD@spéçiäl & characters",
      HKD_special___characters,
      NZD,
      USD,
      date as _airbyte_start_at,
      case when _airbyte_active_row_num = 1 then 1 else 0 end as _airbyte_active_row,
      anyOrNull(date) over (
        partition by id, currency, cast(NZD as String)
        order by
            date is null asc,
            date desc,
            _airbyte_emitted_at desc
            ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING) as _airbyte_end_at,
      _airbyte_ab_id,
      _airbyte_emitted_at,
      _airbyte_dedup_exchange_rate_hashid
    from input_data_with_active_row_num
),
dedup_data as (
    select
        -- we need to ensure de-duplicated rows for merge/update queries
        -- additionally, we generate a unique key for the scd table
        row_number() over (
            partition by
                _airbyte_unique_key,
                _airbyte_start_at,
                _airbyte_emitted_at
            order by _airbyte_active_row desc, _airbyte_ab_id
        ) as _airbyte_row_num,
        assumeNotNull(hex(MD5(
            
                toString(_airbyte_unique_key) || '~' ||
            
            
                toString(_airbyte_start_at) || '~' ||
            
            
                toString(_airbyte_emitted_at)
            
    ))) as _airbyte_unique_key_scd,
        scd_data.*
    from scd_data
)
select
    _airbyte_unique_key,
    _airbyte_unique_key_scd,
    id,
    currency,
    date,
    timestamp_col,
    "HKD@spéçiäl & characters",
    HKD_special___characters,
    NZD,
    USD,
    _airbyte_start_at,
    _airbyte_end_at,
    _airbyte_active_row,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_dedup_exchange_rate_hashid
from dedup_data where _airbyte_row_num = 1
  
    
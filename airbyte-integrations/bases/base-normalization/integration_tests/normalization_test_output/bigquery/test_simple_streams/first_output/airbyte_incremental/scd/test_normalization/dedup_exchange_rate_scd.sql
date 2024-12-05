

  create or replace table `dataline-integration-testing`.test_normalization.`dedup_exchange_rate_scd`
  partition by range_bucket(
            _airbyte_active_row,
            generate_array(0, 1, 1)
        )
  cluster by _airbyte_unique_key_scd, _airbyte_emitted_at
  OPTIONS()
  as (
    
-- depends_on: ref('dedup_exchange_rate_stg')
with

input_data as (
    select *
    from `dataline-integration-testing`._airbyte_test_normalization.`dedup_exchange_rate_stg`
    -- dedup_exchange_rate from `dataline-integration-testing`.test_normalization._airbyte_raw_dedup_exchange_rate
),

scd_data as (
    -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
    select
      to_hex(md5(cast(concat(coalesce(cast(id as 
    string
), ''), '-', coalesce(cast(currency as 
    string
), ''), '-', coalesce(cast(NZD as 
    string
), '')) as 
    string
))) as _airbyte_unique_key,
      id,
      currency,
      date,
      timestamp_col,
      HKD_special___characters,
      HKD_special___characters_1,
      NZD,
      USD,
      date as _airbyte_start_at,
      lag(date) over (
        partition by id, currency, cast(NZD as 
    string
)
        order by
            date is null asc,
            date desc,
            _airbyte_emitted_at desc
      ) as _airbyte_end_at,
      case when row_number() over (
        partition by id, currency, cast(NZD as 
    string
)
        order by
            date is null asc,
            date desc,
            _airbyte_emitted_at desc
      ) = 1 then 1 else 0 end as _airbyte_active_row,
      _airbyte_ab_id,
      _airbyte_emitted_at,
      _airbyte_dedup_exchange_rate_hashid
    from input_data
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
        to_hex(md5(cast(concat(coalesce(cast(_airbyte_unique_key as 
    string
), ''), '-', coalesce(cast(_airbyte_start_at as 
    string
), ''), '-', coalesce(cast(_airbyte_emitted_at as 
    string
), '')) as 
    string
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
    HKD_special___characters,
    HKD_special___characters_1,
    NZD,
    USD,
    _airbyte_start_at,
    _airbyte_end_at,
    _airbyte_active_row,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at,
    _airbyte_dedup_exchange_rate_hashid
from dedup_data where _airbyte_row_num = 1
  );
  
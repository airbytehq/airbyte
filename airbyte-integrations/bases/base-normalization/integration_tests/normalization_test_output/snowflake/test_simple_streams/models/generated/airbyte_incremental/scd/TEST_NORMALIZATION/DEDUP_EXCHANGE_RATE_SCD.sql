{{ config(
    cluster_by = ["_AIRBYTE_ACTIVE_ROW", "_AIRBYTE_UNIQUE_KEY_SCD", "_AIRBYTE_EMITTED_AT"],
    unique_key = "_AIRBYTE_UNIQUE_KEY_SCD",
    schema = "TEST_NORMALIZATION",
    post_hook = ['drop view _AIRBYTE_TEST_NORMALIZATION.DEDUP_EXCHANGE_RATE_STG'],
    tags = [ "top-level" ]
) }}
-- depends_on: ref('DEDUP_EXCHANGE_RATE_STG')
with
{% if is_incremental() %}
new_data as (
    -- retrieve incremental "new" data
    select
        *
    from {{ ref('DEDUP_EXCHANGE_RATE_STG')  }}
    -- DEDUP_EXCHANGE_RATE from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }}
    where 1 = 1
    {{ incremental_clause('_AIRBYTE_EMITTED_AT') }}
),
new_data_ids as (
    -- build a subset of _AIRBYTE_UNIQUE_KEY from rows that are new
    select distinct
        {{ dbt_utils.surrogate_key([
            'ID',
            'CURRENCY',
            'NZD',
        ]) }} as _AIRBYTE_UNIQUE_KEY
    from new_data
),
empty_new_data as (
    -- build an empty table to only keep the table's column types
    select * from new_data where 1 = 0
),
previous_active_scd_data as (
    -- retrieve "incomplete old" data that needs to be updated with an end date because of new changes
    select
        {{ star_intersect(ref('DEDUP_EXCHANGE_RATE_STG'), this, from_alias='inc_data', intersect_alias='this_data') }}
    from {{ this }} as this_data
    -- make a join with new_data using primary key to filter active data that need to be updated only
    join new_data_ids on this_data._AIRBYTE_UNIQUE_KEY = new_data_ids._AIRBYTE_UNIQUE_KEY
    -- force left join to NULL values (we just need to transfer column types only for the star_intersect macro on schema changes)
    left join empty_new_data as inc_data on this_data._AIRBYTE_AB_ID = inc_data._AIRBYTE_AB_ID
    where _AIRBYTE_ACTIVE_ROW = 1
),
input_data as (
    select {{ dbt_utils.star(ref('DEDUP_EXCHANGE_RATE_STG')) }} from new_data
    union all
    select {{ dbt_utils.star(ref('DEDUP_EXCHANGE_RATE_STG')) }} from previous_active_scd_data
),
{% else %}
input_data as (
    select *
    from {{ ref('DEDUP_EXCHANGE_RATE_STG')  }}
    -- DEDUP_EXCHANGE_RATE from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }}
),
{% endif %}
scd_data as (
    -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
    select
      {{ dbt_utils.surrogate_key([
            'ID',
            'CURRENCY',
            'NZD',
      ]) }} as _AIRBYTE_UNIQUE_KEY,
        ID,
        CURRENCY,
        DATE,
        TIMESTAMP_COL,
        {{ adapter.quote('HKD@spéçiäl & characters') }},
        HKD_SPECIAL___CHARACTERS,
        NZD,
        USD,
      DATE as _AIRBYTE_START_AT,
      lag(DATE) over (
        partition by ID, CURRENCY, cast(NZD as {{ dbt_utils.type_string() }})
        order by
            DATE is null asc,
            DATE desc,
            _AIRBYTE_EMITTED_AT desc
      ) as _AIRBYTE_END_AT,
      case when row_number() over (
        partition by ID, CURRENCY, cast(NZD as {{ dbt_utils.type_string() }})
        order by
            DATE is null asc,
            DATE desc,
            _AIRBYTE_EMITTED_AT desc
      ) = 1 then 1 else 0 end as _AIRBYTE_ACTIVE_ROW,
      _AIRBYTE_AB_ID,
      _AIRBYTE_EMITTED_AT,
      _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
    from input_data
),
dedup_data as (
    select
        -- we need to ensure de-duplicated rows for merge/update queries
        -- additionally, we generate a unique key for the scd table
        row_number() over (
            partition by _AIRBYTE_UNIQUE_KEY, _AIRBYTE_START_AT, _AIRBYTE_EMITTED_AT
            order by _AIRBYTE_AB_ID
        ) as _AIRBYTE_ROW_NUM,
        {{ dbt_utils.surrogate_key([
          '_AIRBYTE_UNIQUE_KEY',
          '_AIRBYTE_START_AT',
          '_AIRBYTE_EMITTED_AT'
        ]) }} as _AIRBYTE_UNIQUE_KEY_SCD,
        scd_data.*
    from scd_data
)
select
    _AIRBYTE_UNIQUE_KEY,
    _AIRBYTE_UNIQUE_KEY_SCD,
        ID,
        CURRENCY,
        DATE,
        TIMESTAMP_COL,
        {{ adapter.quote('HKD@spéçiäl & characters') }},
        HKD_SPECIAL___CHARACTERS,
        NZD,
        USD,
    _AIRBYTE_START_AT,
    _AIRBYTE_END_AT,
    _AIRBYTE_ACTIVE_ROW,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from dedup_data where _AIRBYTE_ROW_NUM = 1


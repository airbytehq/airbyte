{{ config(
    unique_key = "{{ quote('_AIRBYTE_UNIQUE_KEY_SCD') }}",
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
with
{% if is_incremental() %}
new_data as (
    -- retrieve incremental "new" data
    select
        *
    from {{ ref('pos_dedup_cdcx_ab3')  }}
    -- pos_dedup_cdcx from {{ source('test_normalization', 'airbyte_raw_pos_dedup_cdcx') }}
    where 1 = 1
    {{ incremental_clause(quote('_AIRBYTE_EMITTED_AT')) }}
),
new_data_ids as (
    -- build a subset of {{ quote('_AIRBYTE_UNIQUE_KEY') }} from rows that are new
    select distinct
        {{ dbt_utils.surrogate_key([
            'id',
        ]) }} as {{ quote('_AIRBYTE_UNIQUE_KEY') }}
    from new_data
),
previous_active_scd_data as (
    -- retrieve "incomplete old" data that needs to be updated with an end date because of new changes
    select
        {{ star_intersect(ref('pos_dedup_cdcx_ab3'), this, from_alias='inc_data', intersect_alias='this_data') }}
    from {{ this }} as this_data
    -- make a join with new_data using primary key to filter active data that need to be updated only
    join new_data_ids on this_data.{{ quote('_AIRBYTE_UNIQUE_KEY') }} = new_data_ids.{{ quote('_AIRBYTE_UNIQUE_KEY') }}
    -- force left join to NULL values (we just need to transfer column types only for the star_intersect macro)
    left join {{ ref('pos_dedup_cdcx_ab3')  }} as inc_data on 1 = 0
    where {{ quote('_AIRBYTE_ACTIVE_ROW') }} = 1
),
input_data as (
    select {{ dbt_utils.star(ref('pos_dedup_cdcx_ab3')) }} from new_data
    union all
    select {{ dbt_utils.star(ref('pos_dedup_cdcx_ab3')) }} from previous_active_scd_data
),
{% else %}
input_data as (
    select *
    from {{ ref('pos_dedup_cdcx_ab3')  }}
    -- pos_dedup_cdcx from {{ source('test_normalization', 'airbyte_raw_pos_dedup_cdcx') }}
),
{% endif %}
scd_data as (
    -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
    select
      {{ dbt_utils.surrogate_key([
            'id',
      ]) }} as {{ quote('_AIRBYTE_UNIQUE_KEY') }},
        id,
        name,
        {{ quote('_AB_CDC_LSN') }},
        {{ quote('_AB_CDC_UPDATED_AT') }},
        {{ quote('_AB_CDC_DELETED_AT') }},
        {{ quote('_AB_CDC_LOG_POS') }},
      {{ quote('_AIRBYTE_EMITTED_AT') }} as {{ quote('_AIRBYTE_START_AT') }},
      lag({{ quote('_AIRBYTE_EMITTED_AT') }}) over (
        partition by id
        order by
            {{ quote('_AIRBYTE_EMITTED_AT') }} asc nulls last,
            {{ quote('_AIRBYTE_EMITTED_AT') }} desc,
            {{ quote('_AIRBYTE_EMITTED_AT') }} desc, {{ quote('_AB_CDC_UPDATED_AT') }} desc, {{ quote('_AB_CDC_LOG_POS') }} desc
      ) as {{ quote('_AIRBYTE_END_AT') }},
      case when lag({{ quote('_AIRBYTE_EMITTED_AT') }}) over (
        partition by id
        order by
            {{ quote('_AIRBYTE_EMITTED_AT') }} asc nulls last,
            {{ quote('_AIRBYTE_EMITTED_AT') }} desc,
            {{ quote('_AIRBYTE_EMITTED_AT') }} desc, {{ quote('_AB_CDC_UPDATED_AT') }} desc, {{ quote('_AB_CDC_LOG_POS') }} desc
      ) is null and {{ quote('_AB_CDC_DELETED_AT') }} is null  then 1 else 0 end as {{ quote('_AIRBYTE_ACTIVE_ROW') }},
      {{ quote('_AIRBYTE_AB_ID') }},
      {{ quote('_AIRBYTE_EMITTED_AT') }},
      {{ quote('_AIRBYTE_POS_DEDUP_CDCX_HASHID') }}
    from input_data
),
dedup_data as (
    select
        -- we need to ensure de-duplicated rows for merge/update queries
        -- additionally, we generate a unique key for the scd table
        row_number() over (
            partition by {{ quote('_AIRBYTE_UNIQUE_KEY') }}, {{ quote('_AIRBYTE_START_AT') }}, {{ quote('_AIRBYTE_EMITTED_AT') }}, cast({{ quote('_AB_CDC_DELETED_AT') }} as {{ dbt_utils.type_string() }}), cast({{ quote('_AB_CDC_UPDATED_AT') }} as {{ dbt_utils.type_string() }}), cast({{ quote('_AB_CDC_LOG_POS') }} as {{ dbt_utils.type_string() }})
            order by {{ quote('_AIRBYTE_AB_ID') }}
        ) as {{ quote('_AIRBYTE_ROW_NUM') }},
        {{ dbt_utils.surrogate_key([
          quote('_AIRBYTE_UNIQUE_KEY'),
          quote('_AIRBYTE_START_AT'),
          quote('_AIRBYTE_EMITTED_AT'), quote('_AB_CDC_DELETED_AT'), quote('_AB_CDC_UPDATED_AT'), quote('_AB_CDC_LOG_POS')
        ]) }} as {{ quote('_AIRBYTE_UNIQUE_KEY_SCD') }},
        scd_data.*
    from scd_data
)
select
    {{ quote('_AIRBYTE_UNIQUE_KEY') }},
    {{ quote('_AIRBYTE_UNIQUE_KEY_SCD') }},
        id,
        name,
        {{ quote('_AB_CDC_LSN') }},
        {{ quote('_AB_CDC_UPDATED_AT') }},
        {{ quote('_AB_CDC_DELETED_AT') }},
        {{ quote('_AB_CDC_LOG_POS') }},
    {{ quote('_AIRBYTE_START_AT') }},
    {{ quote('_AIRBYTE_END_AT') }},
    {{ quote('_AIRBYTE_ACTIVE_ROW') }},
    {{ quote('_AIRBYTE_AB_ID') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ current_timestamp() }} as {{ quote('_AIRBYTE_NORMALIZED_AT') }},
    {{ quote('_AIRBYTE_POS_DEDUP_CDCX_HASHID') }}
from dedup_data where {{ quote('_AIRBYTE_ROW_NUM') }} = 1


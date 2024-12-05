

  create  table
    test_normalization.`nested_stream_with_co_1g_into_long_names_scd__dbt_tmp`
  as (
    
-- depends_on: ref('nested_stream_with_co_1g_into_long_names_stg')
with

input_data as (
    select *
    from _airbyte_test_normalization.`nested_stream_with_co_1g_into_long_names_stg`
    -- nested_stream_with_co__lting_into_long_names from test_normalization._airbyte_raw_nested_s__lting_into_long_names
),

scd_data as (
    -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
    select
      md5(cast(concat(coalesce(cast(id as char), '')) as char)) as _airbyte_unique_key,
      id,
      `date`,
      `partition`,
      `date` as _airbyte_start_at,
      lag(`date`) over (
        partition by id
        order by
            `date` is null asc,
            `date` desc,
            _airbyte_emitted_at desc
      ) as _airbyte_end_at,
      case when row_number() over (
        partition by id
        order by
            `date` is null asc,
            `date` desc,
            _airbyte_emitted_at desc
      ) = 1 then 1 else 0 end as _airbyte_active_row,
      _airbyte_ab_id,
      _airbyte_emitted_at,
      _airbyte_nested_strea__nto_long_names_hashid
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
        md5(cast(concat(coalesce(cast(_airbyte_unique_key as char), ''), '-', coalesce(cast(_airbyte_start_at as char), ''), '-', coalesce(cast(_airbyte_emitted_at as char), '')) as char)) as _airbyte_unique_key_scd,
        scd_data.*
    from scd_data
)
select
    _airbyte_unique_key,
    _airbyte_unique_key_scd,
    id,
    `date`,
    `partition`,
    _airbyte_start_at,
    _airbyte_end_at,
    _airbyte_active_row,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at,
    _airbyte_nested_strea__nto_long_names_hashid
from dedup_data where _airbyte_row_num = 1
  )

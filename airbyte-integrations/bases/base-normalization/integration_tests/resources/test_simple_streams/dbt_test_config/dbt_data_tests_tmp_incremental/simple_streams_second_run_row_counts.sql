with table_row_counts as (
    select distinct '_airbyte_raw_exchange_rate' as label, count(*) as row_count, 6 as expected_count
    from {{ source('test_normalization', '_airbyte_raw_exchange_rate') }}
union all
    select distinct 'exchange_rate' as label, count(*) as row_count, 6 as expected_count
    from {{ ref('exchange_rate') }}

union all

    select distinct '_airbyte_raw_dedup_exchange_rate' as label, count(*) as row_count, 6 as expected_count
    from {{ source('test_normalization', '_airbyte_raw_dedup_exchange_rate') }}
union all
    select distinct 'dedup_exchange_rate_scd' as label, count(*) as row_count, 16 as expected_count
    from {{ ref('dedup_exchange_rate_scd') }}
union all
    select distinct 'dedup_exchange_rate' as label, count(*) as row_count, 7 as expected_count
    from {{ ref('dedup_exchange_rate') }}

union all

    select distinct '_airbyte_raw_dedup_cdc_excluded' as label, count(*) as row_count, 3 as expected_count
    from {{ source('test_normalization', '_airbyte_raw_dedup_cdc_excluded') }}
union all
    select distinct 'dedup_cdc_excluded_scd' as label, count(*) as row_count, 10 as expected_count
    from {{ ref('dedup_cdc_excluded_scd') }}
union all
    select distinct 'dedup_cdc_excluded' as label, count(*) as row_count, 4 as expected_count
    from {{ ref('dedup_cdc_excluded') }}

union all

    select distinct '_airbyte_raw_pos_dedup_cdcx' as label, count(*) as row_count, 6 as expected_count
    from {{ source('test_normalization', '_airbyte_raw_pos_dedup_cdcx') }}
union all
    select distinct 'pos_dedup_cdcx_scd' as label, count(*) as row_count, 8 as expected_count
    from {{ ref('pos_dedup_cdcx_scd') }}
union all
    select distinct 'pos_dedup_cdcx' as label, count(*) as row_count, 3 as expected_count
    from {{ ref('pos_dedup_cdcx') }}
)
select *
from table_row_counts

with table_row_counts as (
    select distinct '_airbyte_raw_exchange_rate' as label, count(*) as row_count, 4 as expected_count
    from {{ source('test_normalization', '_airbyte_raw_exchange_rate') }}
union all
    select distinct 'exchange_rate' as label, count(*) as row_count, 4 as expected_count
    from {{ ref('exchange_rate') }}

union all

    select distinct '_airbyte_raw_dedup_exchange_rate' as label, count(*) as row_count, 10 as expected_count
    from {{ source('test_normalization', '_airbyte_raw_dedup_exchange_rate') }}
union all
    select distinct 'dedup_exchange_rate_scd' as label, count(*) as row_count, 20 as expected_count
    from {{ ref('dedup_exchange_rate_scd') }}
union all
    select distinct 'dedup_exchange_rate' as label, count(*) as row_count, 11 as expected_count
    from {{ ref('dedup_exchange_rate') }}

union all

    select distinct '_airbyte_raw_dedup_cdc_excluded' as label, count(*) as row_count, 4 as expected_count
    from test_normalization._airbyte_raw_dedup_cdc_excluded
union all
    select distinct 'dedup_cdc_excluded_scd' as label, count(*) as row_count, 11 as expected_count
    from test_normalization.dedup_cdc_excluded_scd
union all
    select distinct 'dedup_cdc_excluded' as label, count(*) as row_count, 3 as expected_count
    from test_normalization.dedup_cdc_excluded
)
select *
from table_row_counts

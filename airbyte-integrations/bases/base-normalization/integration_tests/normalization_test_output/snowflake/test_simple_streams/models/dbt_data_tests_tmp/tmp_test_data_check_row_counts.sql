with table_row_counts as (
    select distinct count(*) as row_count, 10 as expected_count
    from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_EXCHANGE_RATE') }}
union all
    select distinct count(*) as row_count, 10 as expected_count
    from {{ ref('EXCHANGE_RATE') }}

union all

    select distinct count(*) as row_count, 10 as expected_count
    from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }}
union all
    select distinct count(*) as row_count, 10 as expected_count
    from {{ ref('DEDUP_EXCHANGE_RATE_SCD') }}
union all
    select distinct count(*) as row_count, 5 as expected_count
    from {{ ref('DEDUP_EXCHANGE_RATE') }}

union all

    select distinct count(*) as row_count, 8 as expected_count
    from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_CDC_EXCLUDED') }}
union all
    select distinct count(*) as row_count, 8 as expected_count
    from {{ ref('DEDUP_CDC_EXCLUDED_SCD') }}
union all
    select distinct count(*) as row_count, 4 as expected_count
    from {{ ref('DEDUP_CDC_EXCLUDED') }}

union all

    select distinct count(*) as row_count, 8 as expected_count
    from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_POS_DEDUP_CDCX') }}
union all
    select distinct count(*) as row_count, 8 as expected_count
    from {{ ref('POS_DEDUP_CDCX_SCD') }}
union all
    select distinct count(*) as row_count, 3 as expected_count
    from {{ ref('POS_DEDUP_CDCX') }}
)
select *
from table_row_counts
where row_count != expected_count

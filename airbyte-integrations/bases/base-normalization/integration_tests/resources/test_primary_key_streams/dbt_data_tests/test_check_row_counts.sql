with table_row_counts as (
    select distinct count(*) as row_count, 7 as expected_count
    from {{ source('test_normalization', '_airbyte_raw_exchange_rate') }}
union all
    select distinct count(*) as row_count, 7 as expected_count
    from {{ ref('test_normalization_exchange_rate') }}

union all

    select distinct count(*) as row_count, 7 as expected_count
    from {{ source('test_normalization', '_airbyte_raw_dedup_exchange_rate') }}
union all
    select distinct count(*) as row_count, 7 as expected_count
    from {{ ref('test_normalization_dedup_exchange_rate_scd') }}
union all
    select distinct count(*) as row_count, 4 as expected_count
    from {{ ref('test_normalization_dedup_exchange_rate') }}
)
select *
from table_row_counts
where row_count != expected_count

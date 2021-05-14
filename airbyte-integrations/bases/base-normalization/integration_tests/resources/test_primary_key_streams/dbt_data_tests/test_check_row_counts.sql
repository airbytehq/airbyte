with table_row_counts as (
    select distinct count(*) as row_count, 7 as expected_count
    from {{ source('test_normalization', '_airbyte_raw_exchange_rate') }}
union all
    select distinct count(*) as row_count, 7 as expected_count
    from {{ ref('exchange_rate_f0e') }}

union all

    select distinct count(*) as row_count, 7 as expected_count
    from {{ source('test_normalization', '_airbyte_raw_dedup_exchange_rate') }}
union all
    select distinct count(*) as row_count, 7 as expected_count
    from {{ ref('dedup_exchange_rate_scd_81d') }}
union all
    select distinct count(*) as row_count, 4 as expected_count
    from {{ ref('dedup_exchange_rate_81d') }}

union all

    select distinct count(*) as row_count, 2 as expected_count
    from {{ source('test_normalization', '_airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names') }}
union all
    select distinct count(*) as row_count, 2 as expected_count
    from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_d67') }}
union all
    select distinct count(*) as row_count, 2 as expected_count
    from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_64a_partition_44f') }}
union all
    select count(distinct currency) as row_count, 1 as expected_count
    from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_669_DATA_886') }}
--union all
--    select count(distinct id) as row_count, 3 as expected_count
--    from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_e78_double_array_data_1b9') }}
)
select *
from table_row_counts
where row_count != expected_count

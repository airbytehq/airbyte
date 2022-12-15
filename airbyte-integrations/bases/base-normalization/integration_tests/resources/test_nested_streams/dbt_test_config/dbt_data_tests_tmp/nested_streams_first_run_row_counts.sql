with table_row_counts as (
    select distinct '_airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names' as label, count(*) as row_count, 2 as expected_count
    from {{ source('test_normalization', '_airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names') }}
union all
    select distinct 'nested_stream_with_complex_columns_resulting_into_long_names' as label, count(*) as row_count, 2 as expected_count
    from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names') }}
union all
    select distinct 'nested_stream_with_complex_columns_resulting_into_long_names_partition' as label, count(*) as row_count, 2 as expected_count
    from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition') }}
union all
    select 'nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA' as label, count(distinct currency) as row_count, 1 as expected_count
    from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA') }}
-- union all
--    select count(distinct id) as row_count, 3 as expected_count
--    from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data') }}
union all
    select 'some_stream_that_was_empty_scd' as label, count(*) as row_count, 0 as expected_count
    from {{ ref('some_stream_that_was_empty_scd') }}
union all
    select 'some_stream_that_was_empty' as label, count(*) as row_count, 0 as expected_count
    from {{ ref('some_stream_that_was_empty') }}
union all
    select 'arrays' as label, count(*) as row_count, 1 as expected_count
    from {{ ref('arrays') }}
union all
    select 'arrays_nested_array_parent' as label, count(*) as row_count, 1 as expected_count
    from {{ ref('arrays_nested_array_parent') }}
)
select *
from table_row_counts

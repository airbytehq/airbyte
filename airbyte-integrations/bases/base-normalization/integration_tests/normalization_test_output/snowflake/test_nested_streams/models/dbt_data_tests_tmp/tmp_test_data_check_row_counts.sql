with table_row_counts as (
    select distinct count(*) as row_count, 2 as expected_count
    from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES') }}
union all
    select distinct count(*) as row_count, 2 as expected_count
    from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES') }}
union all
    select distinct count(*) as row_count, 2 as expected_count
    from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION') }}
union all
    select count(distinct currency) as row_count, 1 as expected_count
    from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA') }}
-- union all
--    select count(distinct id) as row_count, 3 as expected_count
--    from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DOUBLE_ARRAY_DATA') }}
)
select *
from table_row_counts
where row_count != expected_count

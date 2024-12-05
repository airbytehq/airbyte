with table_row_counts as (
    select distinct 'sparse_nested_stream' as label, count(*) as row_count, 1 as expected_count
    from {{ ref('sparse_nested_stream') }}
union all
    select distinct 'sparse_nested_stream_obj_nest1' as label, count(*) as row_count, 1 as expected_count
    from {{ ref('sparse_nested_stream_obj_nest1') }}
union all
    select distinct 'sparse_nested_stream_obj_nest1_obj_nest2' as label, count(*) as row_count, 1 as expected_count
    from {{ ref('sparse_nested_stream_obj_nest1_obj_nest2') }}
union all
    select distinct 'sparse_nested_stream_arr_nest1' as label, count(*) as row_count, 2 as expected_count
    from {{ ref('sparse_nested_stream_arr_nest1') }}
union all
    select distinct 'sparse_nested_stream_arr_nest1_arr_nest2' as label, count(*) as row_count, 4 as expected_count
    from {{ ref('sparse_nested_stream_arr_nest1_arr_nest2') }}
union all
    select distinct 'sparse_nested_stream_empty' as label, count(*) as row_count, 1 as expected_count
    from {{ ref('sparse_nested_stream_empty') }}
union all
    select distinct 'sparse_nested_stream_empty_obj_nest1' as label, count(*) as row_count, 1 as expected_count
    from {{ ref('sparse_nested_stream_empty_obj_nest1') }}
union all
    select distinct 'sparse_nested_stream__y_obj_nest1_obj_nest2' as label, count(*) as row_count, 1 as expected_count
    from {{ ref('sparse_nested_stream__y_obj_nest1_obj_nest2') }}
union all
    select distinct 'sparse_nested_stream_empty_arr_nest1' as label, count(*) as row_count, 2 as expected_count
    from {{ ref('sparse_nested_stream_empty_arr_nest1') }}
union all
    select distinct 'sparse_nested_stream__y_arr_nest1_arr_nest2' as label, count(*) as row_count, 4 as expected_count
    from {{ ref('sparse_nested_stream__y_arr_nest1_arr_nest2') }}
)
select *
from table_row_counts

select * from {{ ref('simple_streams_second_run_row_counts') }}
where row_count != expected_count

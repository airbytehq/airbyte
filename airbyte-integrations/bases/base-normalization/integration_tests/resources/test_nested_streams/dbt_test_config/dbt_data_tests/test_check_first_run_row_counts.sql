select * from {{ ref('nested_streams_first_run_row_counts') }}
where row_count != expected_count

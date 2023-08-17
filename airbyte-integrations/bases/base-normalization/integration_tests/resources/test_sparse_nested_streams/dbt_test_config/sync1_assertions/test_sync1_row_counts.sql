select * from {{ ref('sync1_row_counts') }}
where row_count != expected_count

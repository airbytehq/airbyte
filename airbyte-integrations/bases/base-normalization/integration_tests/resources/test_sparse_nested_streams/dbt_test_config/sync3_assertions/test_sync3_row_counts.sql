select * from {{ ref('sync3_row_counts') }}
where row_count != expected_count

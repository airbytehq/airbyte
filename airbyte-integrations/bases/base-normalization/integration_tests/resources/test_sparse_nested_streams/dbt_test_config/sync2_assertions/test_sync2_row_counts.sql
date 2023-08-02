select * from {{ ref('sync2_row_counts') }}
where row_count != expected_count

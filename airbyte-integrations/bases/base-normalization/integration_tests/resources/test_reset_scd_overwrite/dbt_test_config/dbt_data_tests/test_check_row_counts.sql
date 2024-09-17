select * from {{ ref('test_scd_drop_row_counts') }}
where row_count != expected_count

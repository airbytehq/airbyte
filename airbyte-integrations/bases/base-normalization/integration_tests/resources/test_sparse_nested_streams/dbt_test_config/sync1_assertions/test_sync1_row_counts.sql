select * from {{ ref('SYNC1_ROW_COUNTS') }}
where row_count != expected_count

select * from {{ ref('SYNC2_ROW_COUNTS') }}
where row_count != expected_count

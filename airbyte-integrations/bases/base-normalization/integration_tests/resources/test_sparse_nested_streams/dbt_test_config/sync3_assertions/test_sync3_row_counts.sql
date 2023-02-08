select * from {{ ref('SYNC3_ROW_COUNTS') }}
where row_count != expected_count

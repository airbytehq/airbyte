
      

  create  table "postgres".test_normalization."some_stream_that_was_empty"
  as (
    
-- Final base SQL model
-- depends_on: "postgres".test_normalization."some_stream_that_was_empty_scd"
select
    _airbyte_unique_key,
    "id",
    "date",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_some_stream_that_was_empty_hashid
from "postgres".test_normalization."some_stream_that_was_empty_scd"
-- some_stream_that_was_empty from "postgres".test_normalization._airbyte_raw_some_stream_that_was_empty
where 1 = 1
and _airbyte_active_row = 1

  );
  
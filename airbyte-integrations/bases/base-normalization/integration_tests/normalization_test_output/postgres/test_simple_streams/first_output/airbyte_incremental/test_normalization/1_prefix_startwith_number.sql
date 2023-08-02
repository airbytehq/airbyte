
      

  create  table "postgres".test_normalization."1_prefix_startwith_number"
  as (
    
-- Final base SQL model
-- depends_on: "postgres".test_normalization."1_prefix_startwith_number_scd"
select
    _airbyte_unique_key,
    "id",
    "date",
    "text",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_1_prefix_startwith_number_hashid
from "postgres".test_normalization."1_prefix_startwith_number_scd"
-- 1_prefix_startwith_number from "postgres".test_normalization._airbyte_raw_1_prefix_startwith_number
where 1 = 1
and _airbyte_active_row = 1

  );
  
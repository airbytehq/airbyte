
      

  create  table "postgres".test_normalization."types_testing"
  as (
    
-- Final base SQL model
-- depends_on: "postgres".test_normalization."types_testing_scd"
select
    _airbyte_unique_key,
    "id",
    airbyte_integer_column,
    nullable_airbyte_integer_column,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_types_testing_hashid
from "postgres".test_normalization."types_testing_scd"
-- types_testing from "postgres".test_normalization._airbyte_raw_types_testing
where 1 = 1
and _airbyte_active_row = 1

  );
  
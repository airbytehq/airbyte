
      

  create  table "postgres".test_normalization."multiple_column_names_conflicts"
  as (
    
-- Final base SQL model
-- depends_on: "postgres".test_normalization."multiple_column_names_conflicts_scd"
select
    _airbyte_unique_key,
    "id",
    "User Id",
    user_id,
    "User id",
    "user id",
    "User@Id",
    userid,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_multiple_co__ames_conflicts_hashid
from "postgres".test_normalization."multiple_column_names_conflicts_scd"
-- multiple_column_names_conflicts from "postgres".test_normalization._airbyte_raw_multiple_column_names_conflicts
where 1 = 1
and _airbyte_active_row = 1

  );
  

      

  create  table "postgres".test_normalization."unnest_alias"
  as (
    
-- Final base SQL model
select
    "id",
    children,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_unnest_alias_hashid
from "postgres"._airbyte_test_normalization."unnest_alias_ab3"
-- unnest_alias from "postgres".test_normalization._airbyte_raw_unnest_alias
where 1 = 1

  );
  
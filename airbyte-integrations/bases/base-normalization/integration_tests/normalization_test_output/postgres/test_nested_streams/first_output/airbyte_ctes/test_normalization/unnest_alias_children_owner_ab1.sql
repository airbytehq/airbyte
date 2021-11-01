
  create view "postgres"._airbyte_test_normalization."unnest_alias_children_owner_ab1__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_children_hashid,
    jsonb_extract_path_text("owner", 'owner_id') as owner_id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization."unnest_alias_children" as table_alias
-- owner at unnest_alias/children/owner
where 1 = 1
and "owner" is not null
  );

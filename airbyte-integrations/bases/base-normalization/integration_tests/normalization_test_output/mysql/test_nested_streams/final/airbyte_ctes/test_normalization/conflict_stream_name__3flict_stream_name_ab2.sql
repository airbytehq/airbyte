
  create view _airbyte_test_normalization.`conflict_stream_name__3flict_stream_name_ab2__dbt_tmp` as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_conflict_stream_name_2_hashid,
    cast(`groups` as char) as `groups`,
    _airbyte_emitted_at
from _airbyte_test_normalization.`conflict_stream_name__3flict_stream_name_ab1`
-- conflict_stream_name at conflict_stream_name/conflict_stream_name/conflict_stream_name
  );

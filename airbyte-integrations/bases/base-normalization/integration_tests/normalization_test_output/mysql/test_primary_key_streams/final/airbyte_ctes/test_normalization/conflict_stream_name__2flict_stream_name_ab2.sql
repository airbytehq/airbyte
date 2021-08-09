
  create view _airbyte_test_normalization.`conflict_stream_name__2flict_stream_name_ab2__dbt_tmp` as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_conflict_stream_name_hashid,
    cast(conflict_stream_name as json) as conflict_stream_name,
    _airbyte_emitted_at
from _airbyte_test_normalization.`conflict_stream_name__2flict_stream_name_ab1`
-- conflict_stream_name at conflict_stream_name/conflict_stream_name
  );

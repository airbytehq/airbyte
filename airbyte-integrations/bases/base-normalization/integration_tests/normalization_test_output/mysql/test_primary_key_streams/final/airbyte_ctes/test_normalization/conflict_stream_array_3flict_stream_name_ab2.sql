
  create view _airbyte_test_normalization.`conflict_stream_array_3flict_stream_name_ab2__dbt_tmp` as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_conflict_stream_array_2_hashid,
    cast(id as 
    signed
) as id,
    _airbyte_emitted_at
from _airbyte_test_normalization.`conflict_stream_array_3flict_stream_name_ab1`
-- conflict_stream_name at conflict_stream_array/conflict_stream_array/conflict_stream_name
  );

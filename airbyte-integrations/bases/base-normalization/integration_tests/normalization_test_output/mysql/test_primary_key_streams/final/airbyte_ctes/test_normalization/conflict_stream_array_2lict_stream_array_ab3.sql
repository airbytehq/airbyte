
  create view _airbyte_test_normalization.`conflict_stream_array_2lict_stream_array_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(concat(coalesce(cast(_airbyte_conflict_stream_array_hashid as char), ''), '-', coalesce(cast(conflict_stream_name as char), '')) as char)) as _airbyte_conflict_stream_array_2_hashid
from _airbyte_test_normalization.`conflict_stream_array_2lict_stream_array_ab2`
-- conflict_stream_array at conflict_stream_array/conflict_stream_array
  );

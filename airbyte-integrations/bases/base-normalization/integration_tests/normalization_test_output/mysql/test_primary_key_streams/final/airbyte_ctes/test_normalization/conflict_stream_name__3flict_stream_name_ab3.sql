
  create view _airbyte_test_normalization.`conflict_stream_name__3flict_stream_name_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(concat(coalesce(cast(_airbyte_conflict_stream_name_2_hashid as char), ''), '-', coalesce(cast(`groups` as char), '')) as char)) as _airbyte_conflict_stream_name_3_hashid
from _airbyte_test_normalization.`conflict_stream_name__3flict_stream_name_ab2`
-- conflict_stream_name at conflict_stream_name/conflict_stream_name/conflict_stream_name
  );



  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`conflict_stream_array_conflict_stream_array_conflict_stream_name_ab3`
  OPTIONS()
  as 
-- SQL model to build a hash column based on the values of this record
select
    *,
    to_hex(md5(cast(concat(coalesce(cast(_airbyte_conflict_stream_array_2_hashid as 
    string
), ''), '-', coalesce(cast(id as 
    string
), '')) as 
    string
))) as _airbyte_conflict_stream_name_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`conflict_stream_array_conflict_stream_array_conflict_stream_name_ab2`
-- conflict_stream_name at conflict_stream_array/conflict_stream_array/conflict_stream_name;


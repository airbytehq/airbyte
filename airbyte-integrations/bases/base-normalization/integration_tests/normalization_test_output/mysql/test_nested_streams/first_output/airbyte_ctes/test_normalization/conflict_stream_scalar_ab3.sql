
  create view _airbyte_test_normalization.`conflict_stream_scalar_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(conflict_stream_scalar as char), '')) as char)) as _airbyte_conflict_stream_scalar_hashid,
    tmp.*
from _airbyte_test_normalization.`conflict_stream_scalar_ab2` tmp
-- conflict_stream_scalar
where 1 = 1
  );

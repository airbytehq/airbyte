
  create view _airbyte_test_normalization.`non_nested_stream_wit_1g_into_long_names_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(`date` as char), '')) as char)) as _airbyte_non_nested_s__nto_long_names_hashid,
    tmp.*
from _airbyte_test_normalization.`non_nested_stream_wit_1g_into_long_names_ab2` tmp
-- non_nested_stream_wit__lting_into_long_names
  );

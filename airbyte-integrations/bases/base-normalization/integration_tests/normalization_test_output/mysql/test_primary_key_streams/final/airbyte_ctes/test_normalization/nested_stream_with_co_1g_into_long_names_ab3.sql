
  create view _airbyte_test_normalization.`nested_stream_with_co_1g_into_long_names_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(`date` as char), ''), '-', coalesce(cast(`partition` as char), '')) as char)) as _airbyte_nested_strea__nto_long_names_hashid
from _airbyte_test_normalization.`nested_stream_with_co_1g_into_long_names_ab2`
-- nested_stream_with_co__lting_into_long_names
  );

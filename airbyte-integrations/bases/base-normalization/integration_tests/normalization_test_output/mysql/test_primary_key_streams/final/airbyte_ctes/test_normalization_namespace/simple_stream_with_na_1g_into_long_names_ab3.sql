
  create view _airbyte_test_normalization_namespace.`simple_stream_with_na_1g_into_long_names_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(`date` as char), '')) as char)) as _airbyte_simple_strea__nto_long_names_hashid
from _airbyte_test_normalization_namespace.`simple_stream_with_na_1g_into_long_names_ab2`
-- simple_stream_with_na__lting_into_long_names
  );

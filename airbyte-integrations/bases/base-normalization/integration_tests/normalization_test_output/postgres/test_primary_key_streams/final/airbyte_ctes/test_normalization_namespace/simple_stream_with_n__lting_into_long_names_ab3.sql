
  create view "postgres"._airbyte_test_normalization_namespace."simple_stream_with_n__lting_into_long_names_ab3__dbt_tmp" as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast("id" as 
    varchar
), '') || '-' || coalesce(cast("date" as 
    varchar
), '')

 as 
    varchar
)) as _airbyte_simple_stre__nto_long_names_hashid
from "postgres"._airbyte_test_normalization_namespace."simple_stream_with_n__lting_into_long_names_ab2"
-- simple_stream_with_n__lting_into_long_names
  );

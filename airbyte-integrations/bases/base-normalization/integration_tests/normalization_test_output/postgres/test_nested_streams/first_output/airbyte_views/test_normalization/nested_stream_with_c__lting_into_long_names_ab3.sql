
  create view "postgres"._airbyte_test_normalization."nested_stream_with_c__lting_into_long_names_ab3__dbt_tmp" as (
    
-- SQL model to build a hash column based on the values of this record
select
    md5(cast(coalesce(cast("id" as 
    varchar
), '') || '-' || coalesce(cast("date" as 
    varchar
), '') || '-' || coalesce(cast("partition" as 
    varchar
), '') as 
    varchar
)) as _airbyte_nested_stre__nto_long_names_hashid,
    tmp.*
from "postgres"._airbyte_test_normalization."nested_stream_with_c__lting_into_long_names_ab2" tmp
-- nested_stream_with_c__lting_into_long_names
where 1 = 1

  );

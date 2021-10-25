
  create view "postgres"._airbyte_test_normalization_namespace."simple_stream_with_n__lting_into_long_names_ab2__dbt_tmp" as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast("id" as 
    varchar
) as "id",
    cast("date" as 
    varchar
) as "date",
    _airbyte_emitted_at
from "postgres"._airbyte_test_normalization_namespace."simple_stream_with_n__lting_into_long_names_ab1"
-- simple_stream_with_n__lting_into_long_names
  );

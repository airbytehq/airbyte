
  create view "postgres"._airbyte_test_normalization."nested_stream_with_c__lting_into_long_names_ab2__dbt_tmp" as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast("id" as 
    varchar
) as "id",
    cast("date" as 
    varchar
) as "date",
    cast("partition" as 
    jsonb
) as "partition",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres"._airbyte_test_normalization."nested_stream_with_c__lting_into_long_names_ab1"
-- nested_stream_with_c__lting_into_long_names
where 1 = 1

  );

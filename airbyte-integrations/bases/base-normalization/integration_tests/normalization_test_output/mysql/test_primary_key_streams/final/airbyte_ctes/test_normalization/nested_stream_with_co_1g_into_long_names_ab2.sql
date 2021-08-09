
  create view _airbyte_test_normalization.`nested_stream_with_co_1g_into_long_names_ab2__dbt_tmp` as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as char) as id,
    cast(`date` as char) as `date`,
    cast(`partition` as json) as `partition`,
    _airbyte_emitted_at
from _airbyte_test_normalization.`nested_stream_with_co_1g_into_long_names_ab1`
-- nested_stream_with_co__lting_into_long_names
  );

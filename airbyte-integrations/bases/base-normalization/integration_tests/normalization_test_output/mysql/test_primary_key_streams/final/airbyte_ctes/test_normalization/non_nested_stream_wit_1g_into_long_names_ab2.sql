
  create view _airbyte_test_normalization.`non_nested_stream_wit_1g_into_long_names_ab2__dbt_tmp` as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as char) as id,
    cast(`date` as char) as `date`,
    _airbyte_emitted_at
from _airbyte_test_normalization.`non_nested_stream_wit_1g_into_long_names_ab1`
-- non_nested_stream_wit__lting_into_long_names
  );

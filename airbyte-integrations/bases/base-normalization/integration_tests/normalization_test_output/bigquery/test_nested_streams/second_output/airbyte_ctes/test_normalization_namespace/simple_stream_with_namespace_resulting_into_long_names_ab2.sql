

  create or replace view `dataline-integration-testing`._airbyte_test_normalization_namespace.`simple_stream_with_namespace_resulting_into_long_names_ab2`
  OPTIONS()
  as 
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    string
) as id,
    cast(date as 
    string
) as date,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at
from `dataline-integration-testing`._airbyte_test_normalization_namespace.`simple_stream_with_namespace_resulting_into_long_names_ab1`
-- simple_stream_with_namespace_resulting_into_long_names
where 1 = 1;




  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_ab2`
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
    cast(`partition` as 
    string
) as `partition`,
    _airbyte_emitted_at
from `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_ab1`
-- nested_stream_with_complex_columns_resulting_into_long_names;


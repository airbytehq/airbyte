

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`conflict_stream_scalar_ab2`
  OPTIONS()
  as 
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    string
) as id,
    cast(conflict_stream_scalar as 
    int64
) as conflict_stream_scalar,
    _airbyte_emitted_at
from `dataline-integration-testing`._airbyte_test_normalization.`conflict_stream_scalar_ab1`
-- conflict_stream_scalar;


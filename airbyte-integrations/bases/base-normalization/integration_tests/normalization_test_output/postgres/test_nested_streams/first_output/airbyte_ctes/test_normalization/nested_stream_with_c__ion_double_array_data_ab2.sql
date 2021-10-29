
  create view "postgres"._airbyte_test_normalization."nested_stream_with_c__ion_double_array_data_ab2__dbt_tmp" as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_partition_hashid,
    cast("id" as 
    varchar
) as "id",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres"._airbyte_test_normalization."nested_stream_with_c__ion_double_array_data_ab1"
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
where 1 = 1
  );

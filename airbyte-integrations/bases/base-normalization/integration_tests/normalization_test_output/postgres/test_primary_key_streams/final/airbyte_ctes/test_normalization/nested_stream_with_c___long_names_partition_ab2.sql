
  create view "postgres"._airbyte_test_normalization."nested_stream_with_c___long_names_partition_ab2__dbt_tmp" as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_nested_stre__nto_long_names_hashid,
    double_array_data,
    "DATA",
    "column`_'with""_quotes",
    _airbyte_emitted_at
from "postgres"._airbyte_test_normalization."nested_stream_with_c___long_names_partition_ab1"
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
  );

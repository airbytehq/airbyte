
  create view "postgres"._airbyte_test_normalization."nested_stream_with_c___names_partition_data_ab2__dbt_tmp" as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_partition_hashid,
    cast(currency as 
    varchar
) as currency,
    _airbyte_emitted_at
from "postgres"._airbyte_test_normalization."nested_stream_with_c___names_partition_data_ab1"
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
  );

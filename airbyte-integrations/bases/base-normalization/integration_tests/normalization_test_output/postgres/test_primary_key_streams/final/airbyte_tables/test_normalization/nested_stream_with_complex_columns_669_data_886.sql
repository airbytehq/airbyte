

  create  table "postgres".test_normalization."nested_stream_with_complex_columns_669_data_886__dbt_tmp"
  as (
    
-- Final base SQL model
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_emitted_at,
    _airbyte_data_hashid
from "postgres"._airbyte_test_normalization."nested_stream_with_complex_col_669_data_ab3"
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from "postgres".test_normalization."nested_stream_with_complex_co_64a_partition"
  );
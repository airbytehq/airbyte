

  create  table
    test_normalization.`nested_stream_with_co___names_partition_data__dbt_tmp`
  as (
    
-- Final base SQL model
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at,
    _airbyte_data_hashid
from _airbyte_test_normalization.`nested_stream_with_co_3es_partition_data_ab3`
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from test_normalization.`nested_stream_with_co___long_names_partition`
where 1 = 1
  )

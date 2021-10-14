

  create  table
    test_normalization.`nested_stream_with_co__column___with__quotes__dbt_tmp`
  as (
    
-- Final base SQL model
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_emitted_at,
    _airbyte_column___with__quotes_hashid
from _airbyte_test_normalization.`nested_stream_with_co_3mn___with__quotes_ab3`
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes from test_normalization.`nested_stream_with_co___long_names_partition`
  )

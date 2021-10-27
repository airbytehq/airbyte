

  create or replace table `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes`
  
  
  OPTIONS()
  as (
    
-- Final base SQL model
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_emitted_at,
    _airbyte_column___with__quotes_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes_ab3`
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition`
  );
    
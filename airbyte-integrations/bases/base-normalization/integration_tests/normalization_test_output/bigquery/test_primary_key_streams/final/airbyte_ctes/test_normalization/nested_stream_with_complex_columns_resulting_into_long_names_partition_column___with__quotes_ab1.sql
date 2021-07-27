

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes_ab1`
  OPTIONS()
  as 
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_partition_hashid,
    json_extract_scalar(column___with__quotes, "$['currency']") as currency,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition`
cross join unnest(column___with__quotes) as column___with__quotes
where column___with__quotes is not null
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes;


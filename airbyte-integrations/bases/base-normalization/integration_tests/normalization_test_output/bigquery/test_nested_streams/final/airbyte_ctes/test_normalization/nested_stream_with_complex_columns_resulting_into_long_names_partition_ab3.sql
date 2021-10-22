

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_ab3`
  OPTIONS()
  as 
-- SQL model to build a hash column based on the values of this record
select
    to_hex(md5(cast(concat(coalesce(cast(_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid as 
    string
), ''), '-', coalesce(cast(array_to_string(double_array_data, "|", "") as 
    string
), ''), '-', coalesce(cast(array_to_string(DATA, "|", "") as 
    string
), ''), '-', coalesce(cast(array_to_string(column___with__quotes, "|", "") as 
    string
), '')) as 
    string
))) as _airbyte_partition_hashid,
    tmp.*
from `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2` tmp
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition;


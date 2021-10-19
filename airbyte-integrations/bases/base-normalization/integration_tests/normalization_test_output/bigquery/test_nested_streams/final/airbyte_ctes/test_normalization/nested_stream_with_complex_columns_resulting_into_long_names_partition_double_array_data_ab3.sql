

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab3`
  OPTIONS()
  as 
-- SQL model to build a hash column based on the values of this record
select
    to_hex(md5(cast(concat(coalesce(cast(_airbyte_partition_hashid as 
    string
), ''), '-', coalesce(cast(id as 
    string
), '')) as 
    string
))) as _airbyte_double_array_data_hashid,
    tmp.*
from `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab2` tmp
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data;


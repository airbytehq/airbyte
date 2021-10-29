

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA_ab3`
  OPTIONS()
  as 
-- SQL model to build a hash column based on the values of this record
select
    to_hex(md5(cast(concat(coalesce(cast(_airbyte_partition_hashid as 
    string
), ''), '-', coalesce(cast(currency as 
    string
), '')) as 
    string
))) as _airbyte_DATA_hashid,
    tmp.*
from `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA_ab2` tmp
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
where 1 = 1;


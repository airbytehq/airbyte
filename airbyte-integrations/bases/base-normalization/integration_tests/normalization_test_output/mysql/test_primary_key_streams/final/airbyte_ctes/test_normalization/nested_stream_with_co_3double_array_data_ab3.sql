
  create view _airbyte_test_normalization.`nested_stream_with_co_3double_array_data_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(concat(coalesce(cast(_airbyte_partition_hashid as char), ''), '-', coalesce(cast(id as char), '')) as char)) as _airbyte_double_array_data_hashid
from _airbyte_test_normalization.`nested_stream_with_co_3double_array_data_ab2`
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
  );

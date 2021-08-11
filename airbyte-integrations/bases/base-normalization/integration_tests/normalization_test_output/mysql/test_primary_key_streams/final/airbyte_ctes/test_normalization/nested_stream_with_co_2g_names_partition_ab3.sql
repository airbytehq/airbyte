
  create view _airbyte_test_normalization.`nested_stream_with_co_2g_names_partition_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(concat(coalesce(cast(_airbyte_nested_strea__nto_long_names_hashid as char), ''), '-', coalesce(cast(double_array_data as char), ''), '-', coalesce(cast(`DATA` as char), ''), '-', coalesce(cast(`column__'with"_quotes` as char), '')) as char)) as _airbyte_partition_hashid
from _airbyte_test_normalization.`nested_stream_with_co_2g_names_partition_ab2`
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
  );

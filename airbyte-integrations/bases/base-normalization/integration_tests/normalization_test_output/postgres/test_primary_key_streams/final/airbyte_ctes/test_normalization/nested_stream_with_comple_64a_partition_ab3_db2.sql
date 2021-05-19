
  create view "postgres"._airbyte_test_normalization."nested_stream_with_comple_64a_partition_ab3_db2__dbt_tmp" as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(_airbyte_nested_stre__nto_long_names_hashid as 
    varchar
), '') || '-' || coalesce(cast(double_array_data as 
    varchar
), '') || '-' || coalesce(cast("DATA" as 
    varchar
), '')

 as 
    varchar
)) as _airbyte_partition_hashid
from "postgres"._airbyte_test_normalization."nested_stream_with_comple_64a_partition_ab2"
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
  );

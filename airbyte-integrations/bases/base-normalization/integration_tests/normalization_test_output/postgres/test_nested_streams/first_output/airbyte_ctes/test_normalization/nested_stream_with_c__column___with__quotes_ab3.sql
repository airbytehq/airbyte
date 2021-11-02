
  create view "postgres"._airbyte_test_normalization."nested_stream_with_c__column___with__quotes_ab3__dbt_tmp" as (
    
-- SQL model to build a hash column based on the values of this record
select
    md5(cast(coalesce(cast(_airbyte_partition_hashid as 
    varchar
), '') || '-' || coalesce(cast(currency as 
    varchar
), '') as 
    varchar
)) as _airbyte_column___with__quotes_hashid,
    tmp.*
from "postgres"._airbyte_test_normalization."nested_stream_with_c__column___with__quotes_ab2" tmp
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
where 1 = 1
  );

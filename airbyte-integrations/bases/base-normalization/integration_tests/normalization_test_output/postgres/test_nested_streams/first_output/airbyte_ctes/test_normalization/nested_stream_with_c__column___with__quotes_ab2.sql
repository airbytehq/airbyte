
  create view "postgres"._airbyte_test_normalization."nested_stream_with_c__column___with__quotes_ab2__dbt_tmp" as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_partition_hashid,
    cast(currency as 
    varchar
) as currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres"._airbyte_test_normalization."nested_stream_with_c__column___with__quotes_ab1"
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
where 1 = 1
  );

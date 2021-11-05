

  create  table "postgres".test_normalization."nested_stream_with_c__column___with__quotes__dbt_tmp"
  as (
    
-- Final base SQL model
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_column___with__quotes_hashid
from "postgres"._airbyte_test_normalization."nested_stream_with_c__column___with__quotes_ab3"
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes from "postgres".test_normalization."nested_stream_with_c___long_names_partition"
where 1 = 1
  );
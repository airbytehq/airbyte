
  create view "postgres"._airbyte_test_normalization."nested_stream_with_c__column___with__quotes_ab1__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_partition_hashid,
    jsonb_extract_path_text(_airbyte_nested_data, 'currency') as currency,
    _airbyte_emitted_at
from "postgres".test_normalization."nested_stream_with_c___long_names_partition" as table_alias
cross join jsonb_array_elements(
        case jsonb_typeof("column`_'with""_quotes")
        when 'array' then "column`_'with""_quotes"
        else '[]' end
    ) as _airbyte_nested_data
where "column`_'with""_quotes" is not null
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
  );

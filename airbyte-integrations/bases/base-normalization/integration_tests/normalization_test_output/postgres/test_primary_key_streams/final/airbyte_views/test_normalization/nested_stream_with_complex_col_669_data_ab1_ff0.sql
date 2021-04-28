
  create view "postgres"._airbyte_test_normalization."nested_stream_with_complex_col_669_data_ab1_ff0__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_partition_hashid,
    jsonb_extract_path_text("DATA", 'currency') as currency,
    _airbyte_emitted_at
from "postgres".test_normalization."nested_stream_with_complex_co_64a_partition"
cross join jsonb_array_elements(
        case jsonb_typeof("DATA")
        when 'array' then "DATA"
        else '[]' end
    ) as "DATA"
where "DATA" is not null
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
  );

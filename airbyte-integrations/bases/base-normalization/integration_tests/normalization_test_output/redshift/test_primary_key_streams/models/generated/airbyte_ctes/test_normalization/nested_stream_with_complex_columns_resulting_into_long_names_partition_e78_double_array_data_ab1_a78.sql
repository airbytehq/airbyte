{{ config(alias="nested_stream_with_complex_columns_resulting_into_long_names_partition_e78_double_array_data_ab1", schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnest_cte('nested_stream_with_complex_columns_resulting_into_long_names_64a_partition_44f', 'partition', 'double_array_data') }}
select
    _airbyte_partition_hashid,
    {{ json_extract_scalar(unnested_column_value('double_array_data'), ['id']) }} as id,
    _airbyte_emitted_at
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_64a_partition_44f') }}
{{ cross_join_unnest('partition', 'double_array_data') }}
where double_array_data is not null
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data


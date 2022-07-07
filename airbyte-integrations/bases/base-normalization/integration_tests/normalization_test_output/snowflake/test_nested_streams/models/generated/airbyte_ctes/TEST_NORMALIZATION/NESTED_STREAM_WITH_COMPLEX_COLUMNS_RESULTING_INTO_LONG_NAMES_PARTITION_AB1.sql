{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_SCD') }}
select
    _AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID,
    {{ json_extract_array('PARTITION', ['double_array_data'], ['double_array_data']) }} as DOUBLE_ARRAY_DATA,
    {{ json_extract_array('PARTITION', ['DATA'], ['DATA']) }} as DATA,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_SCD') }} as table_alias
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1
and PARTITION is not null
{{ incremental_clause('_AIRBYTE_EMITTED_AT', this) }}


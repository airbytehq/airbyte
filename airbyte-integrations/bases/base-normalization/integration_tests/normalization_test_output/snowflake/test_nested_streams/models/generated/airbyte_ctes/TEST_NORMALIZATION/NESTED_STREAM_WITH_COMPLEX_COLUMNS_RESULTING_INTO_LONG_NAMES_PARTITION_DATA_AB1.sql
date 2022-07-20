{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION') }}
{{ unnest_cte(ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION'), 'PARTITION', 'DATA') }}
select
    _AIRBYTE_PARTITION_HASHID,
    {{ json_extract_scalar(unnested_column_value('DATA'), ['currency'], ['currency']) }} as CURRENCY,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION') }} as table_alias
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
{{ cross_join_unnest('PARTITION', 'DATA') }}
where 1 = 1
and DATA is not null
{{ incremental_clause('_AIRBYTE_EMITTED_AT', this) }}


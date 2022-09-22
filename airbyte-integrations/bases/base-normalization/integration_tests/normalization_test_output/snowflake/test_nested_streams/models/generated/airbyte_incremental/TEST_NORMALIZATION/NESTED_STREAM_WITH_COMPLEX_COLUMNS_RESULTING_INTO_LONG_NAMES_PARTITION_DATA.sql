{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    schema = "TEST_NORMALIZATION",
    tags = [ "nested" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB3') }}
select
    _AIRBYTE_PARTITION_HASHID,
    CURRENCY,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_DATA_HASHID
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB3') }}
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION') }}
where 1 = 1
{{ incremental_clause('_AIRBYTE_EMITTED_AT', this) }}


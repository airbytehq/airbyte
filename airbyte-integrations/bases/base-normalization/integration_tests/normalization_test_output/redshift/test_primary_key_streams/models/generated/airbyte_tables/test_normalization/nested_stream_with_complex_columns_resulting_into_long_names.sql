{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    date,
    {{ adapter.quote('partition') }},
    _airbyte_emitted_at,
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_scd') }}
-- nested_stream_with_complex_columns_resulting_into_long_names from {{ source('test_normalization', '_airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names') }}
where _airbyte_active_row = 1


{{ config(
    unique_key = "_airbyte_unique_key",
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('nested_stream_with_co_1g_into_long_names_scd') }}
select
    _airbyte_unique_key,
    id,
    {{ adapter.quote('date') }},
    {{ adapter.quote('partition') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_nested_strea__nto_long_names_hashid
from {{ ref('nested_stream_with_co_1g_into_long_names_scd') }}
-- nested_stream_with_co__lting_into_long_names from {{ source('test_normalization', '_airbyte_raw_nested_s__lting_into_long_names') }}
where 1 = 1
and _airbyte_active_row = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}


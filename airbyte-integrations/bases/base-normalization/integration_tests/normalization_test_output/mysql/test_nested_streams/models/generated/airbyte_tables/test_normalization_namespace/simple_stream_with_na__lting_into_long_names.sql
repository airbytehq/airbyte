{{ config(schema="test_normalization_namespace", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    {{ adapter.quote('date') }},
    _airbyte_emitted_at,
    _airbyte_simple_strea__nto_long_names_hashid
from {{ ref('simple_stream_with_na_1g_into_long_names_ab3') }}
-- simple_stream_with_na__lting_into_long_names from {{ source('test_normalization_namespace', '_airbyte_raw_simple_s__lting_into_long_names') }}


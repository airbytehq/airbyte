{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    {{ adapter.quote('id') }},
    children,
    _airbyte_emitted_at,
    _airbyte_unnest_alias_hashid
from {{ ref('unnest_alias_ab3') }}
-- unnest_alias from {{ source('test_normalization', '_airbyte_raw_unnest_alias') }}


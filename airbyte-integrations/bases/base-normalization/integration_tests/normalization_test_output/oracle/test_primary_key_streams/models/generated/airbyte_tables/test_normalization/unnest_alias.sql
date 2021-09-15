{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    children,
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ quote('_AIRBYTE_UNNEST_ALIAS_HASHID') }}
from {{ ref('unnest_alias_ab3') }}
-- unnest_alias from {{ source('test_normalization', 'airbyte_raw_unnest_alias') }}


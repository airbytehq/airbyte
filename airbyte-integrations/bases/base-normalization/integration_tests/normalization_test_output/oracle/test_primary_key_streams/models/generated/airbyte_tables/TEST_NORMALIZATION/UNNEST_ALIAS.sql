{{ config(schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    CHILDREN,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_UNNEST_ALIAS_HASHID') }}
from {{ ref('UNNEST_ALIAS_AB3') }}
-- UNNEST_ALIAS from {{ source('TEST_NORMALIZATION', 'AIRBYTE_RAW_UNNEST_ALIAS') }}


{{ config(schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    CHILDREN,
    _airbyte_emitted_at,
    _AIRBYTE_UNNEST_ALIAS_HASHID
from {{ ref('UNNEST_ALIAS_AB3') }}
-- UNNEST_ALIAS from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_UNNEST_ALIAS') }}


{{ config(schema="TEST_NORMALIZATION", tags=["nested"]) }}
-- Final base SQL model
select
    {{ QUOTE('_AIRBYTE_CHILDREN_HASHID') }},
    OWNER_ID,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_OWNER_HASHID') }}
from {{ ref('UNNEST_ALIAS_CHILDREN_OWNER_AB3') }}
-- OWNER at unnest_alias/children/owner from {{ ref('UNNEST_ALIAS_CHILDREN') }}


{{ config(schema="TEST_NORMALIZATION", tags=["nested"]) }}
-- Final base SQL model
select
    {{ QUOTE('_AIRBYTE_UNNEST_ALIAS_HASHID') }},
    AB_ID,
    OWNER,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_CHILDREN_HASHID') }}
from {{ ref('UNNEST_ALIAS_CHILDREN_AB3') }}
-- CHILDREN at unnest_alias/children from {{ ref('UNNEST_ALIAS') }}


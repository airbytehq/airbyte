{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    {{ QUOTE('_AIRBYTE_CHILDREN_HASHID') }},
    owner_id,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_OWNER_HASHID') }}
from {{ ref('unnest_alias_children_owner_ab3') }}
-- owner at unnest_alias/children/owner from {{ ref('unnest_alias_children') }}


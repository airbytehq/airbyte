{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    {{ quote('_AIRBYTE_CHILDREN_HASHID') }},
    owner_id,
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ quote('_AIRBYTE_OWNER_HASHID') }}
from {{ ref('unnest_alias_children_owner_ab3') }}
-- owner at unnest_alias/children/owner from {{ ref('unnest_alias_children') }}


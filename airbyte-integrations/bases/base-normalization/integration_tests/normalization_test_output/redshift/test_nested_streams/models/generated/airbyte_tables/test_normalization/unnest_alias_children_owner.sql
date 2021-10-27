{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    _airbyte_children_hashid,
    owner_id,
    _airbyte_emitted_at,
    _airbyte_owner_hashid
from {{ ref('unnest_alias_children_owner_ab3') }}
-- owner at unnest_alias/children/owner from {{ ref('unnest_alias_children') }}


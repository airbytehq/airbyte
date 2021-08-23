{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    _airbyte_unnest_alias_hashid,
    ab_id,
    {{ adapter.quote('owner') }},
    _airbyte_emitted_at,
    _airbyte_children_hashid
from {{ ref('unnest_alias_children_ab3') }}
-- children at unnest_alias/children from {{ ref('unnest_alias') }}


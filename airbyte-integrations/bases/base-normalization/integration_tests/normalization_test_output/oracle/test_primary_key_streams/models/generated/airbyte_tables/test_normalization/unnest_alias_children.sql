{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    {{ quote('_AIRBYTE_UNNEST_ALIAS_HASHID') }},
    ab_id,
    owner,
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ quote('_AIRBYTE_CHILDREN_HASHID') }}
from {{ ref('unnest_alias_children_ab3') }}
-- children at unnest_alias/children from {{ ref('unnest_alias') }}


{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ QUOTE('_AIRBYTE_CHILDREN_HASHID') }},
    {{ json_extract_scalar('owner', ['owner_id'], ['owner_id']) }} as owner_id,
    airbyte_emitted_at
from {{ ref('unnest_alias_children') }} 
where owner is not null
-- owner at unnest_alias/children/owner


{{ config(schema="TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ QUOTE('_AIRBYTE_CHILDREN_HASHID') }},
    {{ json_extract_scalar('OWNER', ['owner_id'], ['owner_id']) }} as OWNER_ID,
    airbyte_emitted_at
from {{ ref('UNNEST_ALIAS_CHILDREN') }} 
where OWNER is not null
-- OWNER at unnest_alias/children/owner


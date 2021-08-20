{{ config(schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_children_hashid,
    {{ json_extract_scalar(adapter.quote('owner'), ['owner_id'], ['owner_id']) }} as owner_id,
    _airbyte_emitted_at
from {{ ref('unnest_alias_children') }} as table_alias
where {{ adapter.quote('owner') }} is not null
-- owner at unnest_alias/children/owner


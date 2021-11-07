{{ config(
    cluster_by = "_airbyte_emitted_at",
    partition_by = {"field": "_airbyte_emitted_at", "data_type": "timestamp", "granularity": "day"},
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_airbyte_ab_id'),
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
select
    id,
    children,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_unnest_alias_hashid
from {{ ref('unnest_alias_ab3') }}
-- unnest_alias from {{ source('test_normalization', '_airbyte_raw_unnest_alias') }}
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at') }}


{{ config(
    indexes = [{'columns':['_airbyte_unique_key'],'unique':True}],
    unique_key = "_airbyte_unique_key",
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('1_prefix_startwith_number_scd') }}
select
    _airbyte_unique_key,
    {{ adapter.quote('id') }},
    {{ adapter.quote('date') }},
    {{ adapter.quote('text') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_1_prefix_startwith_number_hashid
from {{ ref('1_prefix_startwith_number_scd') }}
-- 1_prefix_startwith_number from {{ source('test_normalization', '_airbyte_raw_1_prefix_startwith_number') }}
where 1 = 1
and _airbyte_active_row = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}


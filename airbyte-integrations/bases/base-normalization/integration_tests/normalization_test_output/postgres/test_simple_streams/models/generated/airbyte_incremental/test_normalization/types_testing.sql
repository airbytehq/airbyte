{{ config(
    indexes = [{'columns':['_airbyte_unique_key'],'unique':True}],
    unique_key = "_airbyte_unique_key",
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('types_testing_scd') }}
select
    _airbyte_unique_key,
    {{ adapter.quote('id') }},
    airbyte_integer_column,
    nullable_airbyte_integer_column,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_types_testing_hashid
from {{ ref('types_testing_scd') }}
-- types_testing from {{ source('test_normalization', '_airbyte_raw_types_testing') }}
where 1 = 1
and _airbyte_active_row = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}


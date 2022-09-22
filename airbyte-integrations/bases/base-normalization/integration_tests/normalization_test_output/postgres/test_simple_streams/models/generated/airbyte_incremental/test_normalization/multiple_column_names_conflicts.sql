{{ config(
    indexes = [{'columns':['_airbyte_unique_key'],'unique':True}],
    unique_key = "_airbyte_unique_key",
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('multiple_column_names_conflicts_scd') }}
select
    _airbyte_unique_key,
    {{ adapter.quote('id') }},
    {{ adapter.quote('User Id') }},
    user_id,
    {{ adapter.quote('User id') }},
    {{ adapter.quote('user id') }},
    {{ adapter.quote('User@Id') }},
    userid,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_multiple_co__ames_conflicts_hashid
from {{ ref('multiple_column_names_conflicts_scd') }}
-- multiple_column_names_conflicts from {{ source('test_normalization', '_airbyte_raw_multiple_column_names_conflicts') }}
where 1 = 1
and _airbyte_active_row = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}


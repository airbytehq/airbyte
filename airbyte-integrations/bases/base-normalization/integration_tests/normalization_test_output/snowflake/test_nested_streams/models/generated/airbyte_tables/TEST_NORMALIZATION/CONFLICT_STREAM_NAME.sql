{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "TEST_NORMALIZATION",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
select
    ID,
    CONFLICT_STREAM_NAME,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_CONFLICT_STREAM_NAME_HASHID
from {{ ref('CONFLICT_STREAM_NAME_AB3') }}
-- CONFLICT_STREAM_NAME from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_CONFLICT_STREAM_NAME') }}
where 1 = 1


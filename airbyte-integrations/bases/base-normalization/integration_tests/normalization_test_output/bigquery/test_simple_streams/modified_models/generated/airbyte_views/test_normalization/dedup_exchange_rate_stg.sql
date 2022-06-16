{{ config(
    cluster_by = "_airbyte_emitted_at",
    partition_by = {"field": "_airbyte_emitted_at", "data_type": "timestamp", "granularity": "day"},
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('dedup_exchange_rate_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        'id',
        'currency',
        'new_column',
        'date',
        'timestamp_col',
        'HKD_special___characters',
        'NZD',
        'USD',
    ]) }} as _airbyte_dedup_exchange_rate_hashid,
    tmp.*
from {{ ref('dedup_exchange_rate_ab2') }} tmp
-- dedup_exchange_rate
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}


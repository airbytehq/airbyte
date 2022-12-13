{{ config(
    unique_key = '_airbyte_ab_id',
    schema = "test_normalization",
    post_hook = ["
                    {%
                        set scd_table_relation = adapter.get_relation(
                            database=this.database,
                            schema=this.schema,
                            identifier='exchange_rate_scd'
                        )
                    %}
                    {%
                        if scd_table_relation is not none
                    %}
                    {%
                            do adapter.drop_relation(scd_table_relation)
                    %}
                    {% endif %}
                        "],
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('exchange_rate_ab3') }}
select
    id,
    currency,
    {{ adapter.quote('date') }},
    timestamp_col,
    {{ adapter.quote('HKD@spéçiäl & characters') }},
    hkd_special___characters,
    nzd,
    usd,
    {{ adapter.quote('column__\'with"_quotes') }},
    datetime_tz,
    datetime_no_tz,
    time_tz,
    time_no_tz,
    property_binary_data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from {{ ref('exchange_rate_ab3') }}
-- exchange_rate from {{ source('test_normalization', '_airbyte_raw_exchange_rate') }}
where 1 = 1


{{ config(
    unique_key = quote('_AIRBYTE_AB_ID'),
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
    {{ quote('DATE') }},
    timestamp_col,
    hkd_special___characters,
    hkd_special___characters_1,
    nzd,
    usd,
    column___with__quotes,
    datetime_tz,
    datetime_no_tz,
    time_tz,
    time_no_tz,
    property_binary_data,
    {{ quote('_AIRBYTE_AB_ID') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ current_timestamp() }} as {{ quote('_AIRBYTE_NORMALIZED_AT') }},
    {{ quote('_AIRBYTE_EXCHANGE_RATE_HASHID') }}
from {{ ref('exchange_rate_ab3') }}
-- exchange_rate from {{ source('test_normalization', 'airbyte_raw_exchange_rate') }}
where 1 = 1


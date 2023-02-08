{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = '_AIRBYTE_AB_ID',
    schema = "TEST_NORMALIZATION",
    post_hook = ["
                    {%
                        set scd_table_relation = adapter.get_relation(
                            database=this.database,
                            schema=this.schema,
                            identifier='EXCHANGE_RATE_SCD'
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
-- depends_on: {{ ref('EXCHANGE_RATE_AB3') }}
select
    ID,
    CURRENCY,
    DATE,
    TIMESTAMP_COL,
    {{ adapter.quote('HKD@spéçiäl & characters') }},
    HKD_SPECIAL___CHARACTERS,
    NZD,
    USD,
    {{ adapter.quote('column`_\'with""_quotes') }},
    DATETIME_TZ,
    DATETIME_NO_TZ,
    TIME_TZ,
    TIME_NO_TZ,
    PROPERTY_BINARY_DATA,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_EXCHANGE_RATE_HASHID
from {{ ref('EXCHANGE_RATE_AB3') }}
-- EXCHANGE_RATE from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_EXCHANGE_RATE') }}
where 1 = 1




  create view _airbyte_test_normalization.dedup_exchange_rate_stg__dbt_tmp 
  
  as (
    
with __dbt__cte__dedup_exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization._airbyte_raw_dedup_exchange_rate
select
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'id') as id,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'currency') as currency,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'date') as date,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'timestamp_col') as timestamp_col,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'HKD@spéçiäl & characters') as "HKD@spéçiäl & characters",
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'HKD_special___characters') as HKD_special___characters,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'NZD') as NZD,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'USD') as USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from test_normalization._airbyte_raw_dedup_exchange_rate as table_alias
-- dedup_exchange_rate
where 1 = 1

),  __dbt__cte__dedup_exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__dedup_exchange_rate_ab1
select
    accurateCastOrNull(id, '
    BIGINT
') as id,
    nullif(accurateCastOrNull(trim(BOTH '"' from currency), 'String'), 'null') as currency,
    toDate(parseDateTimeBestEffortOrNull(trim(BOTH '"' from nullif(date, '')))) as date,
    parseDateTime64BestEffortOrNull(trim(BOTH '"' from nullif(timestamp_col, ''))) as timestamp_col,
    accurateCastOrNull("HKD@spéçiäl & characters", '
    Float64
') as "HKD@spéçiäl & characters",
    nullif(accurateCastOrNull(trim(BOTH '"' from HKD_special___characters), 'String'), 'null') as HKD_special___characters,
    accurateCastOrNull(NZD, '
    Float64
') as NZD,
    accurateCastOrNull(USD, '
    Float64
') as USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__dedup_exchange_rate_ab1
-- dedup_exchange_rate
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__dedup_exchange_rate_ab2
select
    assumeNotNull(hex(MD5(
            
                toString(id) || '~' ||
            
            
                toString(currency) || '~' ||
            
            
                toString(date) || '~' ||
            
            
                toString(timestamp_col) || '~' ||
            
            
                toString("HKD@spéçiäl & characters") || '~' ||
            
            
                toString(HKD_special___characters) || '~' ||
            
            
                toString(NZD) || '~' ||
            
            
                toString(USD)
            
    ))) as _airbyte_dedup_exchange_rate_hashid,
    tmp.*
from __dbt__cte__dedup_exchange_rate_ab2 tmp
-- dedup_exchange_rate
where 1 = 1

  )
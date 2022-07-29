

  
    create table test_normalization.exchange_rate__dbt_tmp
    
  
    
    engine = MergeTree()
    
    order by (tuple())
    
  as (
    
with __dbt__cte__exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization._airbyte_raw_exchange_rate
select
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'id') as id,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'currency') as currency,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'date') as date,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'timestamp_col') as timestamp_col,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'HKD@spéçiäl & characters') as "HKD@spéçiäl & characters",
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'HKD_special___characters') as HKD_special___characters,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'NZD') as NZD,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'USD') as USD,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'column`_''with\"_quotes') as "column`_'with""_quotes",
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'datetime_tz') as datetime_tz,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'datetime_no_tz') as datetime_no_tz,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'time_tz') as time_tz,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'time_no_tz') as time_no_tz,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from test_normalization._airbyte_raw_exchange_rate as table_alias
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__exchange_rate_ab1
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
    nullif(accurateCastOrNull(trim(BOTH '"' from "column`_'with""_quotes"), 'String'), 'null') as "column`_'with""_quotes",
    parseDateTime64BestEffortOrNull(trim(BOTH '"' from nullif(datetime_tz, ''))) as datetime_tz,
    parseDateTime64BestEffortOrNull(trim(BOTH '"' from nullif(datetime_no_tz, ''))) as datetime_no_tz,
    nullif(accurateCastOrNull(trim(BOTH '"' from time_tz), '
    String
'), 'null') as time_tz,
    nullif(accurateCastOrNull(trim(BOTH '"' from time_no_tz), '
    String
'), 'null') as time_no_tz,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__exchange_rate_ab1
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__exchange_rate_ab2
select
    assumeNotNull(hex(MD5(
            
                toString(id) || '~' ||
            
            
                toString(currency) || '~' ||
            
            
                toString(date) || '~' ||
            
            
                toString(timestamp_col) || '~' ||
            
            
                toString("HKD@spéçiäl & characters") || '~' ||
            
            
                toString(HKD_special___characters) || '~' ||
            
            
                toString(NZD) || '~' ||
            
            
                toString(USD) || '~' ||
            
            
                toString("column`_'with""_quotes") || '~' ||
            
            
                toString(datetime_tz) || '~' ||
            
            
                toString(datetime_no_tz) || '~' ||
            
            
                toString(time_tz) || '~' ||
            
            
                toString(time_no_tz)
            
    ))) as _airbyte_exchange_rate_hashid,
    tmp.*
from __dbt__cte__exchange_rate_ab2 tmp
-- exchange_rate
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__exchange_rate_ab3
select
    id,
    currency,
    date,
    timestamp_col,
    "HKD@spéçiäl & characters",
    HKD_special___characters,
    NZD,
    USD,
    "column`_'with""_quotes",
    datetime_tz,
    datetime_no_tz,
    time_tz,
    time_no_tz,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from __dbt__cte__exchange_rate_ab3
-- exchange_rate from test_normalization._airbyte_raw_exchange_rate
where 1 = 1
  )
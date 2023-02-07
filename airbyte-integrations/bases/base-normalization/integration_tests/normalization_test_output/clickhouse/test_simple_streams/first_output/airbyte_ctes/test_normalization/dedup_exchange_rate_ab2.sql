

  create view _airbyte_test_normalization.dedup_exchange_rate_ab2 
  
  as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: _airbyte_test_normalization.dedup_exchange_rate_ab1
select
    accurateCastOrNull(trim(BOTH '"' from id), '
    BIGINT
') as id,
    nullif(accurateCastOrNull(trim(BOTH '"' from currency), 'String'), 'null') as currency,
    toDate(parseDateTimeBestEffortOrNull(trim(BOTH '"' from nullif(date, '')))) as date,
    parseDateTime64BestEffortOrNull(trim(BOTH '"' from nullif(timestamp_col, ''))) as timestamp_col,
    accurateCastOrNull(trim(BOTH '"' from "HKD@spéçiäl & characters"), '
    Float64
') as "HKD@spéçiäl & characters",
    nullif(accurateCastOrNull(trim(BOTH '"' from HKD_special___characters), 'String'), 'null') as HKD_special___characters,
    accurateCastOrNull(trim(BOTH '"' from NZD), '
    Float64
') as NZD,
    accurateCastOrNull(trim(BOTH '"' from USD), '
    Float64
') as USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from _airbyte_test_normalization.dedup_exchange_rate_ab1
-- dedup_exchange_rate
where 1 = 1

  )
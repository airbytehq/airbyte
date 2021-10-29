

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`dedup_exchange_rate_ab2`
  OPTIONS()
  as 
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    float64
) as id,
    cast(currency as 
    string
) as currency,
    cast(new_column as 
    float64
) as new_column,
    cast(nullif(date, '') as 
    date
) as date,
    cast(nullif(timestamp_col, '') as 
    timestamp
) as timestamp_col,
    cast(HKD_special___characters as 
    float64
) as HKD_special___characters,
    cast(NZD as 
    float64
) as NZD,
    cast(USD as 
    int64
) as USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at
from `dataline-integration-testing`._airbyte_test_normalization.`dedup_exchange_rate_ab1`
-- dedup_exchange_rate
where 1 = 1
;


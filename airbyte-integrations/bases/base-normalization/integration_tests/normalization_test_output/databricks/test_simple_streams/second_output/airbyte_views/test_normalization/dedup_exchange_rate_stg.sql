create or replace view _airbyte_test_normalization.`dedup_exchange_rate_stg`
  
  as
    
with __dbt__cte__dedup_exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization._airbyte_raw_dedup_exchange_rate
select
    get_json_object(_airbyte_data, '$.id') as id,
    get_json_object(_airbyte_data, '$.currency') as currency,
    get_json_object(_airbyte_data, '$.date') as date,
    get_json_object(_airbyte_data, '$.timestamp_col') as timestamp_col,
    get_json_object(_airbyte_data, '$.HKD@spéçiäl & characters') as HKD_special___characters,
    get_json_object(_airbyte_data, '$.HKD_special___characters') as HKD_special___characters_1,
    get_json_object(_airbyte_data, '$.NZD') as NZD,
    get_json_object(_airbyte_data, '$.USD') as USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from test_normalization._airbyte_raw_dedup_exchange_rate as table_alias
-- dedup_exchange_rate
where 1 = 1

),  __dbt__cte__dedup_exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__dedup_exchange_rate_ab1
select
    cast(id as 
    BIGINT
) as id,
    cast(currency as 
    string
) as currency,
    cast(nullif(date, '') as 
    date
) as date,
    cast(nullif(timestamp_col, '') as 
    timestamp
) as timestamp_col,
    cast(HKD_special___characters as 
    float
) as HKD_special___characters,
    cast(HKD_special___characters_1 as 
    string
) as HKD_special___characters_1,
    cast(NZD as 
    float
) as NZD,
    cast(USD as 
    float
) as USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from __dbt__cte__dedup_exchange_rate_ab1
-- dedup_exchange_rate
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__dedup_exchange_rate_ab2
select
    md5(cast(coalesce(cast(id as 
    string
), '') || '-' || coalesce(cast(currency as 
    string
), '') || '-' || coalesce(cast(date as 
    string
), '') || '-' || coalesce(cast(timestamp_col as 
    string
), '') || '-' || coalesce(cast(HKD_special___characters as 
    string
), '') || '-' || coalesce(cast(HKD_special___characters_1 as 
    string
), '') || '-' || coalesce(cast(NZD as 
    string
), '') || '-' || coalesce(cast(USD as 
    string
), '') as 
    string
)) as _airbyte_dedup_exchange_rate_hashid,
    tmp.*
from __dbt__cte__dedup_exchange_rate_ab2 tmp
-- dedup_exchange_rate
where 1 = 1



      create or replace table test_normalization.`exchange_rate`
    
    
    using delta
    
    
    
    
    
    as
      
with __dbt__cte__exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization._airbyte_raw_exchange_rate
select
    get_json_object(_airbyte_data, '$.id') as id,
    get_json_object(_airbyte_data, '$.currency') as currency,
    get_json_object(_airbyte_data, '$.date') as date,
    get_json_object(_airbyte_data, '$.timestamp_col') as timestamp_col,
    get_json_object(_airbyte_data, '$.HKD@spéçiäl & characters') as HKD_special___characters,
    get_json_object(_airbyte_data, '$.HKD_special___characters') as HKD_special___characters_1,
    get_json_object(_airbyte_data, '$.NZD') as NZD,
    get_json_object(_airbyte_data, '$.USD') as USD,
    get_json_object(_airbyte_data, '$.column`_\'with"_quotes') as column___with__quotes,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from test_normalization._airbyte_raw_exchange_rate as table_alias
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__exchange_rate_ab1
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
    cast(column___with__quotes as 
    string
) as column___with__quotes,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from __dbt__cte__exchange_rate_ab1
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__exchange_rate_ab2
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
), '') || '-' || coalesce(cast(column___with__quotes as 
    string
), '') as 
    string
)) as _airbyte_exchange_rate_hashid,
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
    HKD_special___characters,
    HKD_special___characters_1,
    NZD,
    USD,
    column___with__quotes,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from __dbt__cte__exchange_rate_ab3
-- exchange_rate from test_normalization._airbyte_raw_exchange_rate
where 1 = 1
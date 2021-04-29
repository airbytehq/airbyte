

  create  table
    "integrationtests".test_normalization."exchange_rate_f0e__dbt_tmp"
    
    
  as (
    
with __dbt__CTE__exchange_rate_ab1_e8c as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    case when json_extract_path_text(_airbyte_data, 'id', true) != '' then json_extract_path_text(_airbyte_data, 'id', true) end as id,
    case when json_extract_path_text(_airbyte_data, 'currency', true) != '' then json_extract_path_text(_airbyte_data, 'currency', true) end as currency,
    case when json_extract_path_text(_airbyte_data, 'date', true) != '' then json_extract_path_text(_airbyte_data, 'date', true) end as date,
    case when json_extract_path_text(_airbyte_data, 'HKD@spéçiäl & characters', true) != '' then json_extract_path_text(_airbyte_data, 'HKD@spéçiäl & characters', true) end as "hkd@spéçiäl & characters",
    case when json_extract_path_text(_airbyte_data, 'NZD', true) != '' then json_extract_path_text(_airbyte_data, 'NZD', true) end as nzd,
    case when json_extract_path_text(_airbyte_data, 'USD', true) != '' then json_extract_path_text(_airbyte_data, 'USD', true) end as usd,
    _airbyte_emitted_at
from "integrationtests".test_normalization._airbyte_raw_exchange_rate
-- exchange_rate
),  __dbt__CTE__exchange_rate_ab2_e8c as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    bigint
) as id,
    cast(currency as varchar) as currency,
    cast(date as varchar) as date,
    cast("hkd@spéçiäl & characters" as 
    float
) as "hkd@spéçiäl & characters",
    cast(nzd as 
    float
) as nzd,
    cast(usd as 
    float
) as usd,
    _airbyte_emitted_at
from __dbt__CTE__exchange_rate_ab1_e8c
-- exchange_rate
),  __dbt__CTE__exchange_rate_ab3_e8c as (

-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(id as varchar), '') || '-' || coalesce(cast(currency as varchar), '') || '-' || coalesce(cast(date as varchar), '') || '-' || coalesce(cast("hkd@spéçiäl & characters" as varchar), '') || '-' || coalesce(cast(nzd as varchar), '') || '-' || coalesce(cast(usd as varchar), '')

 as varchar)) as _airbyte_exchange_rate_hashid
from __dbt__CTE__exchange_rate_ab2_e8c
-- exchange_rate
)-- Final base SQL model
select
    id,
    currency,
    date,
    "hkd@spéçiäl & characters",
    nzd,
    usd,
    _airbyte_emitted_at,
    _airbyte_exchange_rate_hashid
from __dbt__CTE__exchange_rate_ab3_e8c
-- exchange_rate from "integrationtests".test_normalization._airbyte_raw_exchange_rate
  );
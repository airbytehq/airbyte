
  create view _airbyte_test_normalization.`dedup_exchange_rate_stg__dbt_tmp` as (
    
with __dbt__cte__dedup_exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization._airbyte_raw_dedup_exchange_rate
select
    IF(
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."id"')) = 'null',
        NULL,
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."id"'))
    ) as id,
    IF(
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."currency"')) = 'null',
        NULL,
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."currency"'))
    ) as currency,
    IF(
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."date"')) = 'null',
        NULL,
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."date"'))
    ) as `date`,
    IF(
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."timestamp_col"')) = 'null',
        NULL,
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."timestamp_col"'))
    ) as timestamp_col,
    IF(
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."HKD@spéçiäl & characters"')) = 'null',
        NULL,
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."HKD@spéçiäl & characters"'))
    ) as `HKD@spéçiäl & characters`,
    IF(
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."HKD_special___characters"')) = 'null',
        NULL,
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."HKD_special___characters"'))
    ) as hkd_special___characters,
    IF(
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."NZD"')) = 'null',
        NULL,
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."NZD"'))
    ) as nzd,
    IF(
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."USD"')) = 'null',
        NULL,
        JSON_UNQUOTE(JSON_EXTRACT(_airbyte_data, 
    '$."USD"'))
    ) as usd,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    current_timestamp() as _airbyte_normalized_at
from test_normalization._airbyte_raw_dedup_exchange_rate as table_alias
-- dedup_exchange_rate
where 1 = 1

),  __dbt__cte__dedup_exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__dedup_exchange_rate_ab1
select
    cast(id as 
    signed
) as id,
    cast(currency as char(1000)) as currency,
        case when `date` = '' then NULL
        else cast(`date` as date)
        end as `date`
        ,
    cast(nullif(timestamp_col, '') as char(1000)) as timestamp_col,
    cast(`HKD@spéçiäl & characters` as 
    float
) as `HKD@spéçiäl & characters`,
    cast(hkd_special___characters as char(1000)) as hkd_special___characters,
    cast(nzd as 
    float
) as nzd,
    cast(usd as 
    float
) as usd,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    current_timestamp() as _airbyte_normalized_at
from __dbt__cte__dedup_exchange_rate_ab1
-- dedup_exchange_rate
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__dedup_exchange_rate_ab2
select
    md5(cast(concat(coalesce(cast(id as char(1000)), ''), '-', coalesce(cast(currency as char(1000)), ''), '-', coalesce(cast(`date` as char(1000)), ''), '-', coalesce(cast(timestamp_col as char(1000)), ''), '-', coalesce(cast(`HKD@spéçiäl & characters` as char(1000)), ''), '-', coalesce(cast(hkd_special___characters as char(1000)), ''), '-', coalesce(cast(nzd as char(1000)), ''), '-', coalesce(cast(usd as char(1000)), '')) as char(1000))) as _airbyte_dedup_exchange_rate_hashid,
    tmp.*
from __dbt__cte__dedup_exchange_rate_ab2 tmp
-- dedup_exchange_rate
where 1 = 1

  );
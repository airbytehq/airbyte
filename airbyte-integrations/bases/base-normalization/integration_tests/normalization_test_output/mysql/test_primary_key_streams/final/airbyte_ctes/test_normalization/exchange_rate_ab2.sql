
  create view _airbyte_test_normalization.`exchange_rate_ab2__dbt_tmp` as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    signed
) as id,
    cast(currency as char) as currency,
    cast(`date` as 
    date
) as `date`,
    cast(timestamp_col as char) as timestamp_col,
    cast(`HKD@spéçiäl & characters` as 
    float
) as `HKD@spéçiäl & characters`,
    cast(hkd_special___characters as char) as hkd_special___characters,
    cast(nzd as 
    float
) as nzd,
    cast(usd as 
    float
) as usd,
    _airbyte_emitted_at
from _airbyte_test_normalization.`exchange_rate_ab1`
-- exchange_rate
  );

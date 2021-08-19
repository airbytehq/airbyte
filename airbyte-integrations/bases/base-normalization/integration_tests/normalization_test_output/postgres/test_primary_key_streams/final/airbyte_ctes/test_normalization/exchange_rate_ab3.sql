
  create view "postgres"._airbyte_test_normalization."exchange_rate_ab3__dbt_tmp" as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast("id" as 
    varchar
), '') || '-' || coalesce(cast(currency as 
    varchar
), '') || '-' || coalesce(cast("date" as 
    varchar
), '') || '-' || coalesce(cast(timestamp_col as 
    varchar
), '') || '-' || coalesce(cast("HKD@spéçiäl & characters" as 
    varchar
), '') || '-' || coalesce(cast(hkd_special___characters as 
    varchar
), '') || '-' || coalesce(cast(nzd as 
    varchar
), '') || '-' || coalesce(cast(usd as 
    varchar
), '')

 as 
    varchar
)) as _airbyte_exchange_rate_hashid
from "postgres"._airbyte_test_normalization."exchange_rate_ab2"
-- exchange_rate
  );


  create view _airbyte_test_normalization.`dedup_exchange_rate_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(currency as char), ''), '-', coalesce(cast(`date` as char), ''), '-', coalesce(cast(timestamp_col as char), ''), '-', coalesce(cast(`HKD@spéçiäl & characters` as char), ''), '-', coalesce(cast(hkd_special___characters as char), ''), '-', coalesce(cast(nzd as char), ''), '-', coalesce(cast(usd as char), '')) as char)) as _airbyte_dedup_exchange_rate_hashid
from _airbyte_test_normalization.`dedup_exchange_rate_ab2`
-- dedup_exchange_rate
  );

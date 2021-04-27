

  create  table
    "integrationtests".test_normalization."test_normalization_exchange_rate__dbt_tmp"
    
    
  as (
    
-- Final base SQL model
select
    id,
    currency,
    date,
    hkd,
    nzd,
    usd,
    _airbyte_emitted_at,
    _airbyte_exchange_rate_hashid
from "integrationtests"._airbyte_test_normalization."exchange_rate_ab3"
-- exchange_rate from "integrationtests".test_normalization._airbyte_raw_exchange_rate
  );
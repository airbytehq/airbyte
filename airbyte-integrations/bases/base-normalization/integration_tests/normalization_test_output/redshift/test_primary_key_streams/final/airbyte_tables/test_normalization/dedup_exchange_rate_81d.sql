

  create  table
    "integrationtests".test_normalization."dedup_exchange_rate_81d__dbt_tmp"
    
    
  as (
    
-- Final base SQL model
select
    id,
    currency,
    date,
    "hkd@spéçiäl & characters",
    nzd,
    usd,
    _airbyte_emitted_at,
    _airbyte_dedup_exchange_rate_hashid
from "integrationtests".test_normalization."dedup_exchange_rate_scd"
-- dedup_exchange_rate from "integrationtests".test_normalization._airbyte_raw_dedup_exchange_rate
where _airbyte_active_row = True
  );
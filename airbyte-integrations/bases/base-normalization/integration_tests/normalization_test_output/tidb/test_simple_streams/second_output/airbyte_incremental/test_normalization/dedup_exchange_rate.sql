
      insert into test_normalization.`dedup_exchange_rate` (`_airbyte_unique_key`, `id`, `currency`, `date`, `timestamp_col`, `HKD@spéçiäl & characters`, `hkd_special___characters`, `nzd`, `usd`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_dedup_exchange_rate_hashid`)
    (
       select `_airbyte_unique_key`, `id`, `currency`, `date`, `timestamp_col`, `HKD@spéçiäl & characters`, `hkd_special___characters`, `nzd`, `usd`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_dedup_exchange_rate_hashid`
       from test_normalization.`dedup_exchange_rate__dbt_tmp`
    )
  
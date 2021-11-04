
      insert into test_normalization.exchange_rate ("id", "currency", "date", "timestamp_col", "HKD@spéçiäl & characters", "HKD_special___characters", "NZD", "USD", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_exchange_rate_hashid")
  select "id", "currency", "date", "timestamp_col", "HKD@spéçiäl & characters", "HKD_special___characters", "NZD", "USD", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_exchange_rate_hashid"
  from exchange_rate__dbt_tmp
  
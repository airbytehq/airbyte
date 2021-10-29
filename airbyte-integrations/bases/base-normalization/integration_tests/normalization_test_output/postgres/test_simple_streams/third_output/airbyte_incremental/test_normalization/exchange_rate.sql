
      delete
    from "postgres".test_normalization."exchange_rate"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "exchange_rate__dbt_tmp"
    );

    insert into "postgres".test_normalization."exchange_rate" ("currency", "date", "timestamp_col", "HKD@spéçiäl & characters", "nzd", "usd", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_exchange_rate_hashid", "new_column", "id")
    (
       select "currency", "date", "timestamp_col", "HKD@spéçiäl & characters", "nzd", "usd", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_exchange_rate_hashid", "new_column", "id"
       from "exchange_rate__dbt_tmp"
    );
  
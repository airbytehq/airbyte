
      
    delete from "postgres".test_normalization."dedup_exchange_rate"
    where (_airbyte_unique_key) in (
        select (_airbyte_unique_key)
        from "dedup_exchange_rate__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."dedup_exchange_rate" ("_airbyte_unique_key", "id", "currency", "new_column", "date", "timestamp_col", "HKD@spéçiäl & characters", "nzd", "usd", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_dedup_exchange_rate_hashid")
    (
        select "_airbyte_unique_key", "id", "currency", "new_column", "date", "timestamp_col", "HKD@spéçiäl & characters", "nzd", "usd", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_dedup_exchange_rate_hashid"
        from "dedup_exchange_rate__dbt_tmp"
    )
  
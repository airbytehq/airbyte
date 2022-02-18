
      delete
    from "postgres"._airbyte_test_normalization."dedup_exchange_rate_stg"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "dedup_exchange_rate_stg__dbt_tmp"
    );

    insert into "postgres"._airbyte_test_normalization."dedup_exchange_rate_stg" ("_airbyte_dedup_exchange_rate_hashid", "currency", "date", "timestamp_col", "HKD@spéçiäl & characters", "nzd", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "new_column", "id", "usd")
    (
       select "_airbyte_dedup_exchange_rate_hashid", "currency", "date", "timestamp_col", "HKD@spéçiäl & characters", "nzd", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "new_column", "id", "usd"
       from "dedup_exchange_rate_stg__dbt_tmp"
    );
  
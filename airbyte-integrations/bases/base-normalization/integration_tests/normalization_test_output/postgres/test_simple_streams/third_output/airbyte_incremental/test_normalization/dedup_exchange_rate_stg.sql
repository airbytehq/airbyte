
      
    delete from "postgres"._airbyte_test_normalization."dedup_exchange_rate_stg"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "dedup_exchange_rate_stg__dbt_tmp"
    );
    

    insert into "postgres"._airbyte_test_normalization."dedup_exchange_rate_stg" ("_airbyte_dedup_exchange_rate_hashid", "id", "currency", "new_column", "date", "timestamp_col", "HKD@spéçiäl & characters", "nzd", "usd", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at")
    (
        select "_airbyte_dedup_exchange_rate_hashid", "id", "currency", "new_column", "date", "timestamp_col", "HKD@spéçiäl & characters", "nzd", "usd", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at"
        from "dedup_exchange_rate_stg__dbt_tmp"
    )
  
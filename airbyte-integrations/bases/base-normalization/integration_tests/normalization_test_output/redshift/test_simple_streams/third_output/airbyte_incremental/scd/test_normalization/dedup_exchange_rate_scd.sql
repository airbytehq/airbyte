
      delete
    from "integrationtests".test_normalization."dedup_exchange_rate_scd"
    where (_airbyte_unique_key_scd) in (
        select (_airbyte_unique_key_scd)
        from "dedup_exchange_rate_scd__dbt_tmp"
    );

    insert into "integrationtests".test_normalization."dedup_exchange_rate_scd" ("_airbyte_unique_key", "_airbyte_unique_key_scd", "currency", "date", "timestamp_col", "hkd@spéçiäl & characters", "nzd", "usd", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_dedup_exchange_rate_hashid", "new_column", "id")
    (
       select "_airbyte_unique_key", "_airbyte_unique_key_scd", "currency", "date", "timestamp_col", "hkd@spéçiäl & characters", "nzd", "usd", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_dedup_exchange_rate_hashid", "new_column", "id"
       from "dedup_exchange_rate_scd__dbt_tmp"
    );
  
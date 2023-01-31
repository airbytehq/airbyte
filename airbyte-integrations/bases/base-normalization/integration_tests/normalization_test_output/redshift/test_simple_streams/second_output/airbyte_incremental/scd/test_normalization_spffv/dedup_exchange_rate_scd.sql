
      
    delete from "normalization_tests".test_normalization_spffv."dedup_exchange_rate_scd"
    where (_airbyte_unique_key_scd) in (
        select (_airbyte_unique_key_scd)
        from "dedup_exchange_rate_scd__dbt_tmp"
    );
    

    insert into "normalization_tests".test_normalization_spffv."dedup_exchange_rate_scd" ("_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "currency", "date", "timestamp_col", "hkd@spéçiäl & characters", "hkd_special___characters", "nzd", "usd", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_dedup_exchange_rate_hashid")
    (
        select "_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "currency", "date", "timestamp_col", "hkd@spéçiäl & characters", "hkd_special___characters", "nzd", "usd", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_dedup_exchange_rate_hashid"
        from "dedup_exchange_rate_scd__dbt_tmp"
    )
  
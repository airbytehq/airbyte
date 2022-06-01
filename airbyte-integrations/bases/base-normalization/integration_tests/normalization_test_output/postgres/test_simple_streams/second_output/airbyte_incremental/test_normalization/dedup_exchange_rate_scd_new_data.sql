
      
    delete from "postgres"._airbyte_test_normalization."dedup_exchange_rate_scd_new_data"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "dedup_exchange_rate_scd_new_data__dbt_tmp"
    );
    

    insert into "postgres"._airbyte_test_normalization."dedup_exchange_rate_scd_new_data" ("_airbyte_dedup_exchange_rate_hashid", "id", "currency", "date", "timestamp_col", "HKD@spéçiäl & characters", "hkd_special___characters", "nzd", "usd", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at")
    (
        select "_airbyte_dedup_exchange_rate_hashid", "id", "currency", "date", "timestamp_col", "HKD@spéçiäl & characters", "hkd_special___characters", "nzd", "usd", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at"
        from "dedup_exchange_rate_scd_new_data__dbt_tmp"
    )
  
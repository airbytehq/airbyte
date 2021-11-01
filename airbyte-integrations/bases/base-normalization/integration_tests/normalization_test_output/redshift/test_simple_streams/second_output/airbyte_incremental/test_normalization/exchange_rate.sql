
      delete
    from "integrationtests".test_normalization."exchange_rate"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "exchange_rate__dbt_tmp"
    );

    insert into "integrationtests".test_normalization."exchange_rate" ("id", "currency", "date", "timestamp_col", "hkd@spéçiäl & characters", "hkd_special___characters", "nzd", "usd", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_exchange_rate_hashid")
    (
       select "id", "currency", "date", "timestamp_col", "hkd@spéçiäl & characters", "hkd_special___characters", "nzd", "usd", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_exchange_rate_hashid"
       from "exchange_rate__dbt_tmp"
    );
  
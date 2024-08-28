
      
    delete from "postgres".test_normalization."dedup_cdc_excluded"
    where (_airbyte_unique_key) in (
        select (_airbyte_unique_key)
        from "dedup_cdc_excluded__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."dedup_cdc_excluded" ("_airbyte_unique_key", "id", "name", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_dedup_cdc_excluded_hashid")
    (
        select "_airbyte_unique_key", "id", "name", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_dedup_cdc_excluded_hashid"
        from "dedup_cdc_excluded__dbt_tmp"
    )
  
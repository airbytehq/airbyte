
      
    delete from "postgres".test_normalization."dedup_cdc_excluded_scd"
    where (_airbyte_unique_key_scd) in (
        select (_airbyte_unique_key_scd)
        from "dedup_cdc_excluded_scd__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."dedup_cdc_excluded_scd" ("_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "name", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_dedup_cdc_excluded_hashid")
    (
        select "_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "name", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_dedup_cdc_excluded_hashid"
        from "dedup_cdc_excluded_scd__dbt_tmp"
    )
  

      
    delete from "postgres".test_normalization."pos_dedup_cdcx_scd"
    where (_airbyte_unique_key_scd) in (
        select (_airbyte_unique_key_scd)
        from "pos_dedup_cdcx_scd__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."pos_dedup_cdcx_scd" ("_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "name", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_ab_cdc_log_pos", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_pos_dedup_cdcx_hashid")
    (
        select "_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "name", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_ab_cdc_log_pos", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_pos_dedup_cdcx_hashid"
        from "pos_dedup_cdcx_scd__dbt_tmp"
    )
  
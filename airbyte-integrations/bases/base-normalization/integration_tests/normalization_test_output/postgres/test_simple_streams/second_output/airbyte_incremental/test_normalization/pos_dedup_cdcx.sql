
      
    delete from "postgres".test_normalization."pos_dedup_cdcx"
    where (_airbyte_unique_key) in (
        select (_airbyte_unique_key)
        from "pos_dedup_cdcx__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."pos_dedup_cdcx" ("_airbyte_unique_key", "id", "name", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_ab_cdc_log_pos", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_pos_dedup_cdcx_hashid")
    (
        select "_airbyte_unique_key", "id", "name", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_ab_cdc_log_pos", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_pos_dedup_cdcx_hashid"
        from "pos_dedup_cdcx__dbt_tmp"
    )
  
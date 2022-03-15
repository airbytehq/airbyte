
      
    delete from "postgres"._airbyte_test_normalization."pos_dedup_cdcx_stg"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "pos_dedup_cdcx_stg__dbt_tmp"
    );
    

    insert into "postgres"._airbyte_test_normalization."pos_dedup_cdcx_stg" ("_airbyte_pos_dedup_cdcx_hashid", "id", "name", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_ab_cdc_log_pos", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at")
    (
        select "_airbyte_pos_dedup_cdcx_hashid", "id", "name", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_ab_cdc_log_pos", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at"
        from "pos_dedup_cdcx_stg__dbt_tmp"
    )
  

      
    delete from "postgres"._airbyte_test_normalization."dedup_cdc_excluded_stg"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "dedup_cdc_excluded_stg__dbt_tmp"
    );
    

    insert into "postgres"._airbyte_test_normalization."dedup_cdc_excluded_stg" ("_airbyte_dedup_cdc_excluded_hashid", "id", "name", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at")
    (
        select "_airbyte_dedup_cdc_excluded_hashid", "id", "name", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at"
        from "dedup_cdc_excluded_stg__dbt_tmp"
    )
  
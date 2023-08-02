
      
    delete from "postgres"._airbyte_test_normalization."renamed_dedup_cdc_excluded_stg"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "renamed_dedup_cdc_excluded_stg__dbt_tmp"
    );
    

    insert into "postgres"._airbyte_test_normalization."renamed_dedup_cdc_excluded_stg" ("_airbyte_renamed_dedup_cdc_excluded_hashid", "id", "_ab_cdc_updated_at", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at")
    (
        select "_airbyte_renamed_dedup_cdc_excluded_hashid", "id", "_ab_cdc_updated_at", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at"
        from "renamed_dedup_cdc_excluded_stg__dbt_tmp"
    )
  
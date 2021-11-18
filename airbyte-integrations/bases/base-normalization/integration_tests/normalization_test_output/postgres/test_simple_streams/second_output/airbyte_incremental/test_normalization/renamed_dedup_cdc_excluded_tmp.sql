
      delete
    from "postgres"._airbyte_test_normalization."renamed_dedup_cdc_excluded_tmp"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "renamed_dedup_cdc_excluded_tmp__dbt_tmp"
    );

    insert into "postgres"._airbyte_test_normalization."renamed_dedup_cdc_excluded_tmp" ("_airbyte_renamed_dedup_cdc_excluded_hashid", "id", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at")
    (
       select "_airbyte_renamed_dedup_cdc_excluded_hashid", "id", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at"
       from "renamed_dedup_cdc_excluded_tmp__dbt_tmp"
    );
  
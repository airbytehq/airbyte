
      insert into test_normalization.renamed_dedup_cdc_excluded_scd ("_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "_ab_cdc_updated_at", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_renamed_dedup_cdc_excluded_hashid")
  select "_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "_ab_cdc_updated_at", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_renamed_dedup_cdc_excluded_hashid"
  from renamed_dedup_cdc_excluded_scd__dbt_tmp
  
  
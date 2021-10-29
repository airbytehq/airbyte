
        
        
    

    

    merge into `dataline-integration-testing`.test_normalization.`renamed_dedup_cdc_excluded_scd` as DBT_INTERNAL_DEST
        using (
          select * from `dataline-integration-testing`.test_normalization.`renamed_dedup_cdc_excluded_scd__dbt_tmp`
        ) as DBT_INTERNAL_SOURCE
        on 
            DBT_INTERNAL_SOURCE._airbyte_unique_key_scd = DBT_INTERNAL_DEST._airbyte_unique_key_scd
        

    
    when matched then update set
        `_airbyte_unique_key` = DBT_INTERNAL_SOURCE.`_airbyte_unique_key`,`_airbyte_unique_key_scd` = DBT_INTERNAL_SOURCE.`_airbyte_unique_key_scd`,`id` = DBT_INTERNAL_SOURCE.`id`,`_airbyte_start_at` = DBT_INTERNAL_SOURCE.`_airbyte_start_at`,`_airbyte_end_at` = DBT_INTERNAL_SOURCE.`_airbyte_end_at`,`_airbyte_active_row` = DBT_INTERNAL_SOURCE.`_airbyte_active_row`,`_airbyte_ab_id` = DBT_INTERNAL_SOURCE.`_airbyte_ab_id`,`_airbyte_emitted_at` = DBT_INTERNAL_SOURCE.`_airbyte_emitted_at`,`_airbyte_normalized_at` = DBT_INTERNAL_SOURCE.`_airbyte_normalized_at`,`_airbyte_renamed_dedup_cdc_excluded_hashid` = DBT_INTERNAL_SOURCE.`_airbyte_renamed_dedup_cdc_excluded_hashid`
    

    when not matched then insert
        (`_airbyte_unique_key`, `_airbyte_unique_key_scd`, `id`, `_airbyte_start_at`, `_airbyte_end_at`, `_airbyte_active_row`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_renamed_dedup_cdc_excluded_hashid`)
    values
        (`_airbyte_unique_key`, `_airbyte_unique_key_scd`, `id`, `_airbyte_start_at`, `_airbyte_end_at`, `_airbyte_active_row`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_renamed_dedup_cdc_excluded_hashid`)


  
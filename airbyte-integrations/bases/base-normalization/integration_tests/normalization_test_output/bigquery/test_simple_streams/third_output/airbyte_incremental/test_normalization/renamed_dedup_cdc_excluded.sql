
        
        
    

    

    merge into `dataline-integration-testing`.test_normalization.`renamed_dedup_cdc_excluded` as DBT_INTERNAL_DEST
        using (
          select * from `dataline-integration-testing`.test_normalization.`renamed_dedup_cdc_excluded__dbt_tmp`
        ) as DBT_INTERNAL_SOURCE
        on 
            DBT_INTERNAL_SOURCE._airbyte_unique_key = DBT_INTERNAL_DEST._airbyte_unique_key
        

    
    when matched then update set
        `_airbyte_unique_key` = DBT_INTERNAL_SOURCE.`_airbyte_unique_key`,`id` = DBT_INTERNAL_SOURCE.`id`,`_airbyte_ab_id` = DBT_INTERNAL_SOURCE.`_airbyte_ab_id`,`_airbyte_emitted_at` = DBT_INTERNAL_SOURCE.`_airbyte_emitted_at`,`_airbyte_normalized_at` = DBT_INTERNAL_SOURCE.`_airbyte_normalized_at`,`_airbyte_renamed_dedup_cdc_excluded_hashid` = DBT_INTERNAL_SOURCE.`_airbyte_renamed_dedup_cdc_excluded_hashid`,`name` = DBT_INTERNAL_SOURCE.`name`,`_ab_cdc_lsn` = DBT_INTERNAL_SOURCE.`_ab_cdc_lsn`,`_ab_cdc_updated_at` = DBT_INTERNAL_SOURCE.`_ab_cdc_updated_at`,`_ab_cdc_deleted_at` = DBT_INTERNAL_SOURCE.`_ab_cdc_deleted_at`
    

    when not matched then insert
        (`_airbyte_unique_key`, `id`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_renamed_dedup_cdc_excluded_hashid`, `name`, `_ab_cdc_lsn`, `_ab_cdc_updated_at`, `_ab_cdc_deleted_at`)
    values
        (`_airbyte_unique_key`, `id`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_renamed_dedup_cdc_excluded_hashid`, `name`, `_ab_cdc_lsn`, `_ab_cdc_updated_at`, `_ab_cdc_deleted_at`)


  
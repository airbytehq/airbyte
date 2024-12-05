
        
        
    

    

    merge into `dataline-integration-testing`.test_normalization.`dedup_exchange_rate_scd` as DBT_INTERNAL_DEST
        using (
          select * from `dataline-integration-testing`.test_normalization.`dedup_exchange_rate_scd__dbt_tmp`
        ) as DBT_INTERNAL_SOURCE
        on 
            DBT_INTERNAL_SOURCE._airbyte_unique_key_scd = DBT_INTERNAL_DEST._airbyte_unique_key_scd
        

    
    when matched then update set
        `_airbyte_unique_key` = DBT_INTERNAL_SOURCE.`_airbyte_unique_key`,`_airbyte_unique_key_scd` = DBT_INTERNAL_SOURCE.`_airbyte_unique_key_scd`,`id` = DBT_INTERNAL_SOURCE.`id`,`currency` = DBT_INTERNAL_SOURCE.`currency`,`date` = DBT_INTERNAL_SOURCE.`date`,`timestamp_col` = DBT_INTERNAL_SOURCE.`timestamp_col`,`HKD_special___characters` = DBT_INTERNAL_SOURCE.`HKD_special___characters`,`HKD_special___characters_1` = DBT_INTERNAL_SOURCE.`HKD_special___characters_1`,`NZD` = DBT_INTERNAL_SOURCE.`NZD`,`USD` = DBT_INTERNAL_SOURCE.`USD`,`_airbyte_start_at` = DBT_INTERNAL_SOURCE.`_airbyte_start_at`,`_airbyte_end_at` = DBT_INTERNAL_SOURCE.`_airbyte_end_at`,`_airbyte_active_row` = DBT_INTERNAL_SOURCE.`_airbyte_active_row`,`_airbyte_ab_id` = DBT_INTERNAL_SOURCE.`_airbyte_ab_id`,`_airbyte_emitted_at` = DBT_INTERNAL_SOURCE.`_airbyte_emitted_at`,`_airbyte_normalized_at` = DBT_INTERNAL_SOURCE.`_airbyte_normalized_at`,`_airbyte_dedup_exchange_rate_hashid` = DBT_INTERNAL_SOURCE.`_airbyte_dedup_exchange_rate_hashid`
    

    when not matched then insert
        (`_airbyte_unique_key`, `_airbyte_unique_key_scd`, `id`, `currency`, `date`, `timestamp_col`, `HKD_special___characters`, `HKD_special___characters_1`, `NZD`, `USD`, `_airbyte_start_at`, `_airbyte_end_at`, `_airbyte_active_row`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_dedup_exchange_rate_hashid`)
    values
        (`_airbyte_unique_key`, `_airbyte_unique_key_scd`, `id`, `currency`, `date`, `timestamp_col`, `HKD_special___characters`, `HKD_special___characters_1`, `NZD`, `USD`, `_airbyte_start_at`, `_airbyte_end_at`, `_airbyte_active_row`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_dedup_exchange_rate_hashid`)


  
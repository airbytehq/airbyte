
        
        
    

    

    merge into `dataline-integration-testing`.test_normalization.`unnest_alias` as DBT_INTERNAL_DEST
        using (
          select * from `dataline-integration-testing`.test_normalization.`unnest_alias__dbt_tmp`
        ) as DBT_INTERNAL_SOURCE
        on 
            DBT_INTERNAL_SOURCE._airbyte_ab_id = DBT_INTERNAL_DEST._airbyte_ab_id
        

    
    when matched then update set
        `id` = DBT_INTERNAL_SOURCE.`id`,`children` = DBT_INTERNAL_SOURCE.`children`,`_airbyte_ab_id` = DBT_INTERNAL_SOURCE.`_airbyte_ab_id`,`_airbyte_emitted_at` = DBT_INTERNAL_SOURCE.`_airbyte_emitted_at`,`_airbyte_normalized_at` = DBT_INTERNAL_SOURCE.`_airbyte_normalized_at`,`_airbyte_unnest_alias_hashid` = DBT_INTERNAL_SOURCE.`_airbyte_unnest_alias_hashid`
    

    when not matched then insert
        (`id`, `children`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_unnest_alias_hashid`)
    values
        (`id`, `children`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_unnest_alias_hashid`)


  
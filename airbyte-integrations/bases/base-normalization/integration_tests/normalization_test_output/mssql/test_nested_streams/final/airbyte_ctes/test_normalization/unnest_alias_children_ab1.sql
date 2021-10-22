USE [test_normalization];
    execute('create view _airbyte_test_normalization."unnest_alias_children_ab1__dbt_tmp" as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_unnest_alias_hashid,
    json_value(
    children.value, ''$."ab_id"'') as ab_id,
    json_query(
    children.value, ''$."owner"'') as owner,
    _airbyte_emitted_at
from "test_normalization".test_normalization."unnest_alias" as table_alias

    CROSS APPLY (
	    SELECT [value] = CASE 
			WHEN [type] = 4 THEN (SELECT [value] FROM OPENJSON([value])) 
			WHEN [type] = 5 THEN [value]
			END
	    FROM OPENJSON(children)
    ) AS children
where children is not null
-- children at unnest_alias/children
    ');


-- Note that we cast columns_column to string to avoid any weird numeric equality nonsense.
-- For example, in Postgres, this query returns `true`, even though the two numbers are different: (9223372036854775807 is the max value of a signed 64-bit int)
--   select (9223372036854775807 :: double precision) = (9223372036854775806 :: double precision)
-- Because a double has only 15 decimals of precision, so both values are rounded off to 9.223372036854776e+18

select * from {{ ref('types_testing') }} where
(
  id = 1 and (
    cast(airbyte_integer_column as {{ dbt_utils.type_string() }}) != '9223372036854775807'
    or cast(nullable_airbyte_integer_column as {{ dbt_utils.type_string() }}) != '9223372036854775807'
    {#
    or cast(big_integer_column as {{ dbt_utils.type_string() }}) != '1234567890123456789012345678'
    or cast(nullable_big_integer_column as {{ dbt_utils.type_string() }}) != '1234567890123456789012345678'
    #}
  )
) or (
  id = 2 and (
    cast(airbyte_integer_column as {{ dbt_utils.type_string() }}) != '-9223372036854775808'
    or cast(nullable_airbyte_integer_column as {{ dbt_utils.type_string() }}) != '-9223372036854775808'
    {#
    or cast(big_integer_column as {{ dbt_utils.type_string() }}) != '-1234567890123456789012345678'
    or cast(nullable_big_integer_column as {{ dbt_utils.type_string() }}) != '-1234567890123456789012345678'
    #}
  )
) or (
  id = 3 and (
    cast(airbyte_integer_column as {{ dbt_utils.type_string() }}) != '0'
    or nullable_airbyte_integer_column is not null
    {#
    or cast(big_integer_column as {{ dbt_utils.type_string() }}) != '0'
    or nullable_big_integer_column is not null
    #}
  )
)

select * from {{ ref('types_testing') }} where
(
  id = 1 and (
    cast(property_binary_data as {{ dbt_utils.type_string() }}) != 'dGVzdA=='
  )
) or (
  id = 2 and (
    cast(property_binary_data as {{ dbt_utils.type_string() }}) is not null
  )
) or (
  id = 3 and (
    cast(property_binary_data as {{ dbt_utils.type_string() }}) is not null
  )
)

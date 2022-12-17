select * from {{ ref('types_testing') }} where
(
  id = 1 and (
    cast(property_binary_data as {{ type_binary() }}) != 'test'
  )
) or (
  id = 2 and (
    cast(property_binary_data as {{ type_binary() }}) is not null
  )
) or (
  id = 3 and (
    cast(property_binary_data as {{ type_binary() }}) is not null
  )
)

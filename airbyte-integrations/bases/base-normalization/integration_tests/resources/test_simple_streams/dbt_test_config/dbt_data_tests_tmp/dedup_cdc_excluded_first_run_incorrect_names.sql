select * from {{ ref('dedup_cdc_excluded') }} where
(
  id = 1 and name != 'mazda'
) or (
  id = 2 and name != 'toyata'
) or (
  id = 5 and name != 'vw'
) or (
  id = 7 and name != 'lotus'
) or (
  id = 8 and name != 'foo3'
) or (
  id not in (1, 2, 5, 7, 8)
)

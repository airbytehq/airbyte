# Just a quick list of schemas that had problems:
- accessories
- consumables
- hardware
- locations
- consumables
- users
- licenses
- categories
- manufacturers

# Multiple fields across `hardware.json` are declared as non-nullable but show up as null in production.
```python
--------------------------------------------------------------------------------
None is not of type 'string'

Failed validating 'type' in schema['properties']['purchase_cost']:
    {'example': '1114.86', 'type': 'string'}

On instance['purchase_cost']:
    None
```
# The above is true for multiple schemas. A few examples:
```python
--------------------------------------------------------------------------------
None is not of type 'string'

Failed validating 'type' in schema['properties']['model_number']:
    {'type': 'string'}

On instance['model_number']:
    None
```

# In the `hardware.json` schema, "custom_fields" field was listed as "array", but shows up in production as an "object"
```python
--------------------------------------------------------------------------------
{'Office Equipment': {'field': '_snipeit_office_equipment_25', 'value': 'IT Equipment', 'field_format': 'ANY'}, 'Screen Display': {'field': '_snipeit_screen_display_36', 'value': 'LED', 'field_format': 'ANY'}, 'Screen Size (Inches)': {'field': '_snipeit_screen_size_inches_37', 'value': '24', 'field_format': 'ANY'}} is not of type 'array'

Failed validating 'type' in schema['properties']['custom_fields']:
    {'type': 'array'}

On instance['custom_fields']:
    {'Office Equipment': {'field': '_snipeit_office_equipment_25',
                          'field_format': 'ANY',
                          'value': 'IT Equipment'},
     'Screen Display': {'field': '_snipeit_screen_display_36',
                        'field_format': 'ANY',
                        'value': 'LED'},
     'Screen Size (Inches)': {'field': '_snipeit_screen_size_inches_37',
                              'field_format': 'ANY',
                              'value': '24'}}
```

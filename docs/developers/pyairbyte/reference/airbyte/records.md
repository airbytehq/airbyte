---
id: airbyte-records
title: airbyte.records
---

Module airbyte.records
======================
PyAirbyte Records module.

## Understanding record handling in PyAirbyte

PyAirbyte models record handling after Airbyte's "Destination V2" ("Dv2") record handling. This
includes the below implementation details.

### Field Name Normalization

1. PyAirbyte normalizes top-level record keys to lowercase, replacing spaces and hyphens with
   underscores.
2. PyAirbyte does not normalize nested keys on sub-properties.

For example, the following record:

```json
{

    "My-Field": "value",
    "Nested": {
        "MySubField": "value"
    }
}
```

Would be normalized to:

```json
{
    "my_field": "value",
    "nested": {
        "MySubField": "value"
    }
}
```

### Table Name Normalization

Similar to column handling, PyAirbyte normalizes table names to the lowercase version of the stream
name and may remove or normalize special characters.

### Airbyte-Managed Metadata Columns

PyAirbyte adds the following columns to every record:

- `ab_raw_id`: A unique identifier for the record.
- `ab_extracted_at`: The time the record was extracted.
- `ab_meta`: A dictionary of extra metadata about the record.

The names of these columns are included in the `airbyte.constants` module for programmatic
reference.

## Schema Evolution

PyAirbyte supports a very basic form of schema evolution:

1. Columns are always auto-added to cache tables whenever newly arriving properties are detected
   as not present in the cache table.
2. Column types will not be modified or expanded to fit changed types in the source catalog.
   - If column types change, we recommend user to manually alter the column types.
3. At any time, users can run a full sync with a `WriteStrategy` of 'replace'. This will create a
   fresh table from scratch and then swap the old and new tables after table sync is complete.

---

Classes
-------

`StreamRecord(from_dict: dict, *, stream_record_handler: StreamRecordHandler, with_internal_columns: bool = True, extracted_at: datetime | None = None)`
:   The StreamRecord class is a case-aware, case-insensitive dictionary implementation.
    
    It has these behaviors:
    - When a key is retrieved, deleted, or checked for existence, it is always checked in a
      case-insensitive manner.
    - The original case is stored in a separate dictionary, so that the original case can be
      retrieved when needed.
    - Because it is subclassed from `dict`, the `StreamRecord` class can be passed as a normal
      Python dictionary.
    - In addition to the properties of the stream's records, the dictionary also stores the Airbyte
      metadata columns: `_airbyte_raw_id`, `_airbyte_extracted_at`, and `_airbyte_meta`.
    
    This behavior mirrors how a case-aware, case-insensitive SQL database would handle column
    references.
    
    There are two ways this class can store keys internally:
    - If normalize_keys is True, the keys are normalized using the given normalizer.
    - If normalize_keys is False, the original case of the keys is stored.
    
    In regards to missing values, the dictionary accepts an 'expected_keys' input. When set, the
    dictionary will be initialized with the given keys. If a key is not found in the input data, it
    will be initialized with a value of None. When provided, the 'expected_keys' input will also
    determine the original case of the keys.
    
    Initialize the dictionary with the given data.
    
    Args:
        from_dict: The dictionary to initialize the StreamRecord with.
        stream_record_handler: The StreamRecordHandler to use for processing the record.
        with_internal_columns: If `True`, the internal columns will be added to the record.
        extracted_at: The time the record was extracted. If not provided, the current time will
            be used.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Static methods

    `from_record_message(record_message: AirbyteRecordMessage, *, stream_record_handler: StreamRecordHandler)`
    :   Return a StreamRecord from a RecordMessage.

`StreamRecordHandler(*, json_schema: dict, normalizer: type[NameNormalizerBase] = airbyte._util.name_normalizers.LowerCaseNormalizer, normalize_keys: bool = False, prune_extra_fields: bool)`
:   A class to handle processing of StreamRecords.
    
    This is a long-lived object that can be used to process multiple StreamRecords, which
    saves on memory and processing time by reusing the same object for all records of the same type.
    
    Initialize the dictionary with the given data.
    
    Args:
        json_schema: The JSON Schema definition for this stream.
        normalizer: The normalizer to use when normalizing keys. If not provided, the
            LowerCaseNormalizer will be used.
        normalize_keys: If `True`, the keys will be normalized using the given normalizer.
        prune_extra_fields: If `True`, unexpected fields will be removed.

    ### Methods

    `to_display_case(self, key: str) ‑> str`
    :   Return the original case of the key.
        
        If the key is not found in the pretty case lookup, return the key provided.

    `to_index_case(self, key: str) ‑> str`
    :   Return the internal case of the key.
        
        If `normalize_keys` is True, returns the normalized key.
        Otherwise, return the original case ("pretty case") of the key.
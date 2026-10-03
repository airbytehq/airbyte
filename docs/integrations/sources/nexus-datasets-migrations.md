# Infor Nexus Datasets Source Migration Guide

## Upgrading to 0.2.0

This version introduces dynamic schema discovery and changes the record structure.

### What changed

1. **Record structure change**: Records previously returned in a wrapped format with `raw_data` (object) and `raw_data_string` (string) fields. Records are now returned as flat objects with individual fields matching the dataset's schema as defined in the Infor Nexus Analytics model.

2. **Schema discovery**: The connector now fetches the schema dynamically from the Infor Nexus Analytics model API at discover time. The model name is automatically resolved from the dataset metadata — no additional configuration is needed.

3. **Removed config field**: The `dataset_model_name` field is no longer required or exposed in the connector spec. The model is resolved automatically from the dataset name.

### Migration steps

1. **Refresh source schema**: After upgrading, go to your connection settings and click "Refresh source schema" to pick up the new dynamically discovered fields.

2. **Reset affected streams**: Because the record structure has changed from wrapped to flat, you must clear (reset) all streams to avoid schema conflicts in your destination.

### Who is affected

There are zero production connections at time of release, so no existing users are impacted.

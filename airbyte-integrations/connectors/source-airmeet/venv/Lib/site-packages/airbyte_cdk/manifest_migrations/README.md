# Manifest Migrations

This directory contains the logic and registry for manifest migrations in the Airbyte CDK. Migrations are used to update or transform manifest components to newer formats or schemas as the CDK evolves.

## Adding a New Migration

1. **Create a Migration File:**
   - Add a new Python file in the `migrations/` subdirectory.
   - Name the file using the pattern: `<description_of_the_migration>.py`.
     - Example: `http_requester_url_base_to_url.py`
   - The filename should be unique and descriptive.

2. **Define the Migration Class:**
   - The migration class must inherit from `ManifestMigration`.
   - Name the class using a descriptive name (e.g., `HttpRequesterUrlBaseToUrl`).
   - Implement the following methods:
     - `should_migrate(self, manifest: ManifestType) -> bool`
     - `migrate(self, manifest: ManifestType) -> None`
     - `validate(self, manifest: ManifestType) -> bool`

3. **Register the Migration:**
   - Open `migrations/registry.yaml`.
   - Add an entry under the appropriate version, or create a new version section if needed.
     - Version can be: "*", "==6.48.3", "~=1.2", ">=1.0.0,<2.0.0", "6.48.3"
   - Each migration entry should include:
     - `name`: The filename (without `.py`)
     - `order`: The order in which this migration should be applied for the version
     - `description`: A short description of the migration

   Example:

   ```yaml
   manifest_migrations:
     - version: 6.45.2
       migrations:
         - name: http_requester_url_base_to_url
           order: 1
           description: |
             This migration updates the `url_base` field in the `HttpRequester` component spec to `url`.
   ```

4. **Testing:**
   - Ensure your migration is covered by unit tests.
   - Tests should verify both `should_migrate`, `migrate`, and `validate` behaviors.

## Migration Discovery

- Migrations are discovered and registered automatically based on the entries in `migrations/registry.yaml`.
- Do not modify the migration registry in code manually.
- If you need to skip certain component types, use the `NON_MIGRATABLE_TYPES` list in `manifest_migration.py`.

## Example Migration Skeleton

```python
from airbyte_cdk.manifest_migrations.manifest_migration import TYPE_TAG, ManifestMigration, ManifestType

class ExampleMigration(ManifestMigration):
    component_type = "ExampleComponent"
    original_key = "old_key"
    replacement_key = "new_key"

    def should_migrate(self, manifest: ManifestType) -> bool:
        return manifest[TYPE_TAG] == self.component_type and self.original_key in manifest

    def migrate(self, manifest: ManifestType) -> None:
        manifest[self.replacement_key] = manifest[self.original_key]
        manifest.pop(self.original_key, None)

    def validate(self, manifest: ManifestType) -> bool:
        return self.replacement_key in manifest and self.original_key not in manifest
```

---

For more details, see the docstrings in `manifest_migration.py` and the examples in the `migrations/` folder.

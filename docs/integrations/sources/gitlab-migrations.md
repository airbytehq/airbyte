# Gitlab Migration Guide

## Upgrading to 2.0.0


Following 2.0.0 config change, we are changing field format to `date-time` for following fields `pipeline.created_at` and `pipeline.updated_at` in Deployments stream, `expires_at` in Group Members and Project Members streams as Gitlab API docs declares. This is a breaking change as `format` was changed. You will need to refresh the source schema and reset affected streams after upgrading.

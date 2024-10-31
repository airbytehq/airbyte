# Paystack Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 has a schema change.

The refunds schema has been changed it's 'type' in schema['properties']['fully_deducted'] to integer. Destination should be aware of this change.

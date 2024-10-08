# MailerLite Migration Guide

## Upgrading to 1.0.0

The version migrates the MailerLite connector to the be compatible with connector builder.
Important:
 - The forms_popup stream schema from API has a breaking change to schema['properties']['settings']['properties']['schedule'] field to contain booleans instead of strings,
 - The forms_promotion stream schema from API has a breaking change to schema['properties']['double_optin'], schema['properties']['settings']['properties']['schedule'] fields to contain booleans instead of strings"

## Connector Upgrade Guide

The destination should be ready to receive the current 1.0.0 updates of schema changes 
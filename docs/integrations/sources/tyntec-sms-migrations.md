import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Tyntec SMS Migration Guide

## Upgrading to 0.3.0

Version 0.3.0 removes the `contacts`, `phones` and `registrations` streams and changes the connection check to use the `sms` stream.

### What changed

- The `contacts`, `phones` and `registrations` streams no longer exist.
- The connection check now calls the `sms` stream (the [Send SMS](https://api.tyntec.com/reference/sms/current.html#sms-api-Send%20SMS%20(GET)) endpoint) instead of the removed `phones` stream.
- The `sms` and `messages` streams are unchanged.

### Why this changed

The removed streams read from tyntec's BYON (Bring Your Own Number) endpoints `/byon/contacts/v1`, `/byon/phonebook/v1/numbers` and `/byon/provisioning/v1`. tyntec's API gateway no longer routes these paths and answers `404 {"message":"no Route matched with those values"}` for every request, so the streams could never return data. Because the connection check used the `phones` stream, every connection test also failed and the connector could not be set up at all.

### Who is affected

All users of the connector are affected by the connection-check change (it is what makes the connector usable again). Users who had the `contacts`, `phones` or `registrations` streams selected in a connection must remove them.

### Required actions

1. Upgrade the connector to 0.3.0.
2. Open each connection that uses this source and refresh the source schema; deselect or remove the `contacts`, `phones` and `registrations` streams if they are still listed.
3. If those streams had created tables in your destination, drop them manually if you no longer need them.
4. Re-test the source. Note that the connection check and every sync send the configured SMS message from `from` to `to`.

## Connector upgrade guide

<MigrationGuide />

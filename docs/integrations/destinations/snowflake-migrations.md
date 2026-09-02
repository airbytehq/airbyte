# Snowflake Migration Guide

## Upgrading to 5.0.0

Username and password authentication is removed in this version. Key Pair Authentication is the only
supported authentication method.

Snowflake is enforcing MFA for password-based service users as part of its
[MFA rollout](https://docs.snowflake.com/en/user-guide/security-mfa-rollout). This change affects only
destinations configured with Username and Password. Destinations configured with Key Pair Authentication
are not affected and do not need any action.

Before upgrading:

1. Generate an RSA key pair using the
   [Snowflake key-pair authentication guide](https://docs.snowflake.com/en/user-guide/key-pair-auth).
2. Register the public key on your Snowflake user:

   ```sql
   ALTER USER <user> SET RSA_PUBLIC_KEY='...'
   ```

3. Edit the destination in Airbyte, select Key Pair Authentication, paste the private key and optional
   passphrase, then test and save the destination.
4. Upgrade the destination after reconfiguring it.

After the upgrade deadline, connections that still use password authentication are disabled until you
reconfigure them. This change does not modify data or tables. You do not need to clear or refresh any
connections.

## Upgrading to 4.0.0

This version upgrades Destination Snowflake to the [Direct-Load](/platform/using-airbyte/core-concepts/direct-load-tables) paradigm, which improves performance and reduces warehouse spend. If you have unusual requirements around record visibility or schema evolution, read that document for more information about how direct-load differs from Typing and Deduping.

This version also adds an option to enable CDC deletions as soft-deletes.

The connector now requires `ALTER TABLE` permissions to support schema evolution and table modifications. Grant your Snowflake user this permission before upgrading.

If you do not interact with the raw tables, you can safely upgrade. There is no breakage for this usecase.

If you _only_ interact with the raw tables, make sure that you have the `Disable Final Tables` option enabled before upgrading. This will automatically enable the `Legacy raw tables` option after upgrading.

If you interact with both the raw _and_ final tables, this usecase will no longer be directly supported. You must create two connectors (one with `Disable Final Tables` enabled, and one with it disabled) and run two connections in parallel.

## Upgrading to 3.0.0

This version introduces [Destinations V2](/release_notes/self-managed/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides better error handling, incremental delivery of data for large syncs, and improved final table structures. To review the breaking changes, and how to upgrade, see the [quick start to upgrading](/release_notes/self-managed/upgrading_to_destinations_v2/#quick-start-to-upgrading). These changes will likely require updates to downstream dbt / SQL models, which we walk through in the [downstream transformations guide](/release_notes/self-managed/upgrading_to_destinations_v2/#updating-downstream-transformations). Selecting `Upgrade` will upgrade **all** connections using this destination at their next sync. You can manually sync existing connections prior to the next scheduled sync to start the upgrade early.

Worthy of specific mention, this version includes:

- Per-record error handling
- Clearer table structure
- Removal of sub-tables for nested properties
- Removal of SCD tables

Learn more about what's new in Destinations V2 in the [Typing & Deduping guide](/platform/using-airbyte/core-concepts/typing-deduping).

## Upgrading to 2.0.0

Snowflake no longer supports GCS/S3. Please migrate to the Internal Staging option. This is recommended by Snowflake and is cheaper and faster.

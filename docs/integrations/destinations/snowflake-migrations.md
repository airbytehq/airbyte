# Snowflake Migration Guide

## Upgrading to 5.0.0

This version deprecates username and password authentication. Username and password authentication will be removed in a future release. **Key pair authentication** is now the only recommended method for connecting to Snowflake. This aligns with [Snowflake's deprecation of single-factor password sign-ins](https://docs.snowflake.com/en/user-guide/security-mfa-rollout), which is enforcing strong authentication for all users on a rolling per-account basis between **August and October 2026**.

### Who is affected

If your Airbyte connection to Snowflake uses **username and password** credentials, you must migrate to key pair authentication before Snowflake enforces strong authentication on your account (rolling between August and October 2026). Connections that already use key pair authentication are not affected. No clear or refresh is required; existing destination data and sync state are unaffected.

### Migration steps

1. **Generate a key pair** if you don't already have one:

   ```bash
   # Generate an unencrypted private key
   openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt

   # Generate the matching public key
   openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
   ```

   Alternatively, to generate an encrypted private key:

   ```bash
   openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -v2 aes-256-cbc -out rsa_key.p8
   ```

   For a complete guide on key pair setup including key storage and verification, see [Step 1: Set up key pair authentication](./snowflake#step-1-set-up-key-pair-authentication) in the setup guide.

2. **Assign the public key to your Snowflake user.** Run this SQL in Snowflake. Replace `<user_name>` with the Snowflake username configured in your Airbyte connection (you can find this on the destination configuration page in the Airbyte UI) and `<public_key_value>` with the contents of your `rsa_key.pub` file, **excluding** the `-----BEGIN PUBLIC KEY-----` and `-----END PUBLIC KEY-----` header/footer lines:

   ```sql
   ALTER USER <user_name> SET rsa_public_key='<public_key_value>';
   ```

   This command requires the `ACCOUNTADMIN` role, or a custom role with the `MODIFY PROGRAMMATIC AUTHENTICATION METHODS` privilege on that specific user. For more information, see [ALTER USER ... MODIFY PROGRAMMATIC AUTHENTICATION METHODS](https://docs.snowflake.com/en/sql-reference/sql/alter-user-modify-programmatic-access-token) in the Snowflake docs.

3. **Update the connection in Airbyte.** Edit the Snowflake destination settings in the Airbyte UI:
   - Change the authentication method to **Key Pair Authentication**.
   - Paste the contents of your `rsa_key.p8` private key file, without removing the header or footer lines.
   - If you used an encrypted key, enter the passphrase in the **Passphrase** field.
   - Save and test the connection.

4. **(Optional) Remove the password from the Snowflake user** once you've confirmed the key pair connection works:

   ```sql
   ALTER USER <user_name> UNSET PASSWORD;
   ```

5. **(Optional) Set the user type to SERVICE** to indicate this is a programmatic service account:

   ```sql
   ALTER USER <user_name> SET TYPE = SERVICE;
   ```

If you're having trouble migrating to key pair authentication before Snowflake enforces strong authentication on your account, you can request an extension of the enforcement date from Snowflake. In Snowsight, go to **Trust Center** > **Strong Authentication** (`https://app.snowflake.com/<org_id>/<account>/#/trust-center/overview/strong-authentication`, replacing `<org_id>` and `<account>` with your Snowflake organization and account identifiers).

For more details on key pair authentication troubleshooting, see [Snowflake's troubleshooting docs](https://docs.snowflake.com/en/user-guide/key-pair-auth-troubleshooting).

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

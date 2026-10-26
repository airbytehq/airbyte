# Snowflake Migration Guide

## Upgrading to 2.0.0

This version deprecates username and password authentication. Username and password authentication will be removed in a future release. **Key pair authentication** or a **programmatic access token** is now the recommended method for connecting to Snowflake. This aligns with [Snowflake's deprecation of single-factor password sign-ins](https://docs.snowflake.com/en/user-guide/security-mfa-rollout), which is enforcing strong authentication for all users on a rolling per-account basis between **August and October 2026**.

### Who is affected

If your Airbyte Snowflake source uses **username and password** credentials, you must migrate to key pair authentication or a programmatic access token before Snowflake enforces strong authentication on your account (rolling between August and October 2026). Sources that already use key pair or programmatic access token authentication are not affected. No reset or full refresh is required; existing sync state is unaffected.

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

   For a complete guide on key pair setup including key storage and verification, see [Key pair authentication](./snowflake.md#key-pair-authentication) in the setup guide.

2. **Assign the public key to your Snowflake user.** Run this SQL in Snowflake. Replace `<user_name>` with the Snowflake username configured in your Airbyte source (you can find this on the source configuration page in the Airbyte UI) and `<public_key_value>` with the contents of your `rsa_key.pub` file, **excluding** the `-----BEGIN PUBLIC KEY-----` and `-----END PUBLIC KEY-----` header/footer lines:

   ```sql
   ALTER USER <user_name> SET rsa_public_key='<public_key_value>';
   ```

   This command requires the `ACCOUNTADMIN` role, or a custom role with the `MODIFY PROGRAMMATIC AUTHENTICATION METHODS` privilege on that specific user. For more information, see [ALTER USER ... MODIFY PROGRAMMATIC AUTHENTICATION METHODS](https://docs.snowflake.com/en/sql-reference/sql/alter-user-modify-programmatic-access-token) in the Snowflake docs.

3. **Update the source in Airbyte.** Edit the Snowflake source settings in the Airbyte UI:
   - Change the authorization method to **Key Pair Authentication**.
   - Paste the contents of your `rsa_key.p8` private key file, without removing the header or footer lines.
   - If you used an encrypted key, enter the passphrase in the **Passphrase** field.
   - Save and test the source.

4. **(Optional) Remove the password from the Snowflake user** once you've confirmed the key pair connection works:

   ```sql
   ALTER USER <user_name> UNSET PASSWORD;
   ```

5. **(Optional) Set the user type to SERVICE** to indicate this is a programmatic service account:

   ```sql
   ALTER USER <user_name> SET TYPE = SERVICE;
   ```

If you prefer a programmatic access token instead of a key pair, follow [Programmatic access token authentication](./snowflake.md#programmatic-access-token-authentication) in the setup guide and select **Programmatic Access Token** as the authorization method.

If you're having trouble migrating to key pair authentication before Snowflake enforces strong authentication on your account, you can request an extension of the enforcement date from Snowflake. In Snowsight, go to **Trust Center** > **Strong Authentication** (`https://app.snowflake.com/<org_id>/<account>/#/trust-center/overview/strong-authentication`, replacing `<org_id>` and `<account>` with your Snowflake organization and account identifiers).

For more details on key pair authentication troubleshooting, see [Snowflake's troubleshooting docs](https://docs.snowflake.com/en/user-guide/key-pair-auth-troubleshooting).

## Upgrading to 1.0.0

This version introduces Airbyte certified source connector for Snowflake to replace the community supported source connector.

**THIS VERSION INCLUDES BREAKING CHANGES FROM PREVIOUS VERSIONS OF THE CONNECTOR!**

### What to expect when upgrading:

1. No change to full refresh sync mode.
2. If you're using incremental sync mode, the incremental sync will trigger a one-time full refresh sync on the first run after upgrade because the old connection state will not be compatible with the new connector. After the full refresh the new state will be populated and the incremental sync will work as expected.

### Migration steps:
No extra actions are required to set up the new connector. The new connector configuration spec is backwards compatible with the community supported version.
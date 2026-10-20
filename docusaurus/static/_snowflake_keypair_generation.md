To configure key pair authentication, you need a private/public key pair. This method uses an RSA key pair (minimum 2048-bit) instead of a password to authenticate with Snowflake. If you don't have a key pair yet, you can generate one using the `openssl` command line tool. For full details, see [Snowflake's key-pair authentication documentation](https://docs.snowflake.com/en/user-guide/key-pair-auth).

#### 1. Generate a private key

Open a terminal and run one of the following commands to generate a private key in PKCS#8 PEM format.

**Unencrypted key** (simpler setup, no passphrase required at connection time):

```bash
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
```

**Encrypted key** (recommended for production -- protects the key file with a passphrase):

```bash
openssl genrsa 2048 | openssl pkcs8 -topk8 -v2 aes-256-cbc -inform PEM -out rsa_key.p8
```

Airbyte also supports encrypted keys generated with `-v2 des3`, as documented by Snowflake. Airbyte supports other key-pair formats and algorithms supported by Snowflake -- see [Snowflake's key-pair authentication documentation](https://docs.snowflake.com/en/user-guide/key-pair-auth) for the full list. You can also optionally set up [key rotation](https://docs.snowflake.com/en/user-guide/key-pair-auth#configuring-key-pair-rotation) for zero-downtime key replacement.

:::tip
Snowflake recommends using an encrypted private key and a passphrase that complies with your organization's security standards. Store the passphrase in a secure location -- it is only used locally and is never sent to Snowflake.
:::

#### 2. Generate the matching public key

Derive the public key from the private key you just created:

```bash
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
```

#### 3. Store the keys securely

Copy both key files to a secure local directory. Protect the private key file with appropriate file-system permissions. It is your responsibility to secure the key when it is not in use.

If you need help troubleshooting key pair authentication, see [Snowflake's troubleshooting docs](https://docs.snowflake.com/en/user-guide/key-pair-auth-troubleshooting).

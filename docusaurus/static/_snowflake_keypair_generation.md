To configure key pair authentication, you need a private/public key pair. If you don't have the key pair yet, you can generate one using the openssl command line tool. Use this command to generate an unencrypted private key file:

`openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt`

Alternatively, use this command to generate an encrypted private key file:

`openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -v2 aes-256-cbc -out rsa_key.p8`

 Once you have your private key, you need to generate a matching public key. You can do so with the following command:

`openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub`

Finally, you need to add the public key to your Snowflake user account. You can do so with the following SQL command in Snowflake. Replace `<user_name>` with your user name and `<public_key_value>` with your public key.

`alter user <user_name> set rsa_public_key=<public_key_value>;`

If you need help troubleshooting key pair authentication, see [Snowflake's troubleshooting docs](https://docs.snowflake.com/en/user-guide/key-pair-auth-troubleshooting).

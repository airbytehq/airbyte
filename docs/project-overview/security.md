# Security and Data Privacy at Airbyte

## Data Security

Airbyte provides a secure environment for customers and users that protects all user data following industry standard practices. From day 1, we have designed and adapted our product with security as a part of the foundation. An independent third-party completed a SOC2 Type 2 assessment and found effective operational controls in place.

Below we have detailed information on various parts of our security practices.

**Flow of Customer Data**

Airbyte extracts data from client data sources (API, file, database) and loads it into their destination platforms (warehouse, data lake). Optional transformation can be done at the client’s data destination. Think of Airbyte as the pipes moving data from Point A to point B.

**Data Retention**

Client data, besides the data listed below, is not stored or cached in Airbyte infrastructure. As soon as data has transferred from the Source to the Destination, it is purged from Airbyte infrastructure.

We store: 

1. Technical Logs 
   
Technical logs are stored for troubleshooting purposes. Logs are limited to metadata and do not contain customer’s data. 

2. Configuration Metadata

Airbyte retains configuration details and data points such as table and column names for each integration. This information is used to configure data replication (i.e. so Airbyte knows what data to sync). It is also used in the UI so that a user can configure their sync.

3. Encrypted Credentials

Most Airbyte Connectors require keys, secrets, or passwords. In Airbyte Cloud, this data is fetched and encrypted using https and stored in Google Secret Manager. We store this encrypted data so that client Connectors can continually sync without prompting credentials on every refresh. When persisting connector configurations to disk or the database, we store a version of the configuration that points to the secret in Google Secret Manager instead of the secret itself to limit the parts of the system that interact with secrets. OSS users deploy their own instance of Airbyte, and Airbyte as a company cannot access these secrets. GCP OSS users may opt to use Google Secrets Manager, otherwise we encourage OSS users to secure their Airbyte data as much as possible.

## Encryption

All Cloud Connectors (APIs, files, databases) pull data through encrypted channels (SSL, SSH tunnel, HTTPS) and the data transfer between our clients' infrastructure and Airbyte infrastructure is fully encrypted. Some users may elect to whitelist our server IPs to allow them to access their DB server behind a firewall. This is an optional opt-in process. In OSS, there are some Connectors that allow unencrypted data transfer (ex. when pulling from a local database) where data is never transiting the public internet or transiting to Airbyte.

## User Authentication [Airbyte Cloud]

**Password Logins**

For Cloud customers, Airbyte requires that Passwords be at least 6 characters, and users will be locked out after multiple failed attempts. This can be overcome by resetting the password.

**OAuth**

For our Cloud customers, we will soon offer the option to use OAuth and sign in with single sign-on.

## Human Interaction with Infrastructure

Only certain qualified Airbyte staff are able to access Airbyte infrastructure and technical logs for deployments, upgrades, configuration changes, and troubleshooting. 

## Sensitive Data

Currently, Airbyte does not knowingly ingest any sensitive data (ex. PII, PHI, Credit Card, EU personal data, minors), and does not handle any sensitive data separately. In the future, we may offer the ability to mask or exclude columns so that no sensitive data arrives in the client’s warehouse. Clients are required to follow our Terms of Services, and are ultimately responsible for ensuring their data transfer is compliant in their jurisdiction.


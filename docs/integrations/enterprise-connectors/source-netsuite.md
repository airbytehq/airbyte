---
dockerRepository: airbyte/source-netsuite-enterprise
---
# Source Netsuite

Airbyte’s incubating Netsuite enterprise source connector currently offers Full Refresh and cursosr-based Incremental syncs for streams.

## Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |

## Prequisities

- Dedicated read-only Airbyte user with read-only access to tables needed for replication
- A Netsuite environment using **SuiteAnalytics Connect** and the **Netsuite2.com** data source for integrations
- Airbyte does not support connecting over SSL using custom Certificate Authority (CA)

## Setup Guide

### Requirements

- **Host:** Service hostname
- **Port:** Service port (Typically 1708)
- **Account ID:** Identifies the Netsuite account (not the individual user account)
- **Authentication method:** Select between username and password or token based authentication to connect with a Netsuite user account to connect with Airbyte. See details below.
- **Role**: A user role with sufficient access on Netsuite for all tables to be replicated and is assigned to the user account

To find details such as host, port, Account ID and role go on Netsuite home page, scroll down to Settings at the bottom left and click "Set Up SuiteAnalytics Connect".

![Netsuite Setup](/assets/docs/enterprise-connectors/netsuite-setup.png)

Note: the role controls what is visible and not to the connector. At a minimum the "SuiteAnalytics Connect" permission is required to connect to SuiteAnalytics over JDBC, as described in [Netsuite SuiteAnalytics documentations](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4102771016.html#To-set-up-SuiteAnalytics-Connect-permissions-using-Manage-Roles%3A)

### Authentication Methods
Source Netsuite supports all authentication methods in SuiteAnalytics connect: username and password, Token Based Authentication (TBA) and OAuth 2.0 based authenticaiton.
#### Username and Password
Fill in the username and password of the Netsuite user account.
Ensure that the Role ID is assigned to this user (this can be done in the Netsuite UI by navigating to Setup > Users/Roles > Manage Users and selecting the user). The role must have sufficient permissions to access all the tables you want to replicate.

#### Token Based Authentication (TBA)
Airbyte requires the following details in order to set up TBA:
- **Client ID (Consumer Key)**
- **Client Secret (Consumer Secret)**
- **Token ID**
- **Token Secret**

The values are generated on netsuite as follows:
1. Confirm the following features are enabled in Netsuite (Setup > Company > Enable Features > SuiteCloud)
   - Client SuiteScript
   - Server SuiteScript
   - Token Based Authentication
2. Create an Integration Record (Setup > Integration > Manage Integrations > New)
   - Check the "Token Based Authentication" box only. (No need for TBA Authorization Flow)
   - Upon creation copy and save the Consumer Key and Consumer Secret.
3. Create an access token (Setup > Users/Roles > Access Tokens > New)
   - Select the application you just created - this is the integration record name created in step 2.
   - Select the user you want to use for the token. This user must have a role with the "Log in using Access Tokens" permission, in addition to "SuiteAnalytics Connect".
   - Select the role you want to use for the token. **This would typically be the "Data Warehouse Integrator" role**.
   - Upon creation copy and save the Token ID and Token Secret values.
4. On the Airbyte source-netsuite's config page fill-in the Client ID, Client Secret, Token ID and Token Secret values and the role ID for the role the token was created for in step 3.
5. Confirm Netsuite is accessible by clicking the "Test and save" button.

#### OAuth 2.0 Based Authentication
Airbyte requires the following details in order to set up OAuth 2.0 Based Authentication:
- **Client ID (Consumer Key)**
- **Certificate ID**
- **Private Key**

The process of setting up OAuth 2.0 for Netsuite SuiteAnalytics Connect is as follows:
1. Confirm the following features are enabled in Netsuite (Setup > Company > Enable Features > SuiteCloud)
    - Client SuiteScript
    - Server SuiteScript
    - OAUTH 2.0
2. Create an Integration Record (Setup > Integration > Manage Integrations > New)
    - Under OAuth 2.0 Check the "Client Credentials (Machine to Machine) Grant" box only. (No need for Authorization Code grant)
    - Check the "SuiteAnalytics Connect" scope.
    - Upon creation copy and save the Consumer Key.
3. Set Permission (Setup > Users/Roles > Manage Users)
    - Select or create the user you want to use for the token. This user must have a role with the "Log in using Access Tokens" permission, in addition to "SuiteAnalytics Connect".
    - Select or create the role you want to use for the token. **This would typically be the "Data Warehouse Integrator" role**.
4. Generate or upload the public key of a public/private key pair to Netsuite (Setup > Integration > Manage Authentication > OAuth 2.0 Client Credentials Setup)
    - In case you need to generate a new key pair, the following OpenSSL command can be used:
      ```bash
            openssl req -new -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -pkeyopt ec_param_enc:named_curve -nodes -days 365 -out public.pem -keyout private.pem
      ```
      Airbyte supports all key types supported by Netsuite.
    - Upload the public key to Netsuite and save the Certificate ID.
5. On the Airbyte source-netsuite's config page fill-in the Consumer key, Certificate ID and the role ID for the role the token was created or selected in step 3.
6. Upload the private key that was generated in step 4.
7. Confirm Netsuite is accessible by clicking the "Test and save" button.

Please consult the [Netsuite OAuth 2.0 for Connect documentation](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/article_0907012138.html) for further details.







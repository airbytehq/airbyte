---
sidebar_label: Microsoft Entra ID
products: cloud-teams, oss-enterprise
---

# Set up single sign on using Microsoft Entra ID

This guide shows you how to set up Microsoft Entra ID (formerly Azure ActiveDirectory) and Airbyte so your users can log into Airbyte using your organization's identity provider (IdP) using OpenID Connect (OIDC). 

## Overview

This guide is for administrators. It assumes you have:

- Basic knowledge of Entra ID, OIDC, and Airbyte
- The permissions to manage Entra ID in your organization
- The permissions to manage Airbyte in your organization

The exact process differs between the Cloud or Self-Managed versions of Airbyte. Steps for both are below.

## Cloud with Teams add-on

### Create application

You will need to create a new Entra ID application for Airbyte. Log into the [Azure Portal](https://portal.azure.com/) and search for the Entra ID service.

From the overview page of Entra ID, press **Add** > **App registration** on the top of the screen.

Specify any name you want (e.g. "Airbyte") and configure a **Redirect URI** of type **Web** with the following value:

```
https://cloud.airbyte.com/auth/realms/<your-company-identifier>/broker/default/endpoint
```

Hit **Register** to create the application.

### Create Client credentials

To create Client credentials for Airbyte to talk to your application head to **Certificates & Secrets** on the detail screen of your application and select the **Client secrets** tab.

Click **New client secret**, specify any Description you want and any expiry date you want.

:::tip
We recommend to chose an expiry date of at least 12 months. You'll need to pass in the new client secret every time the old one expires to continue being able to log in via Entra ID.
:::

Copy the **Value** (the Client Secret itself) immediately after creation. You won't be able to view this later on.

### Setup information needed

You'll need to pass your Airbyte contact the following information of the created application.

- **Client Secret**: as copied above
- **Application (client) ID**: You'll find this in the **Essentials** section on the **Overview** page of the application you created
- **OpenID Connect metadata document**: You'll find this in the **Endpoints** panel, that you can open from the top bar on the **Overview** page
- **Email Domain**: Users signing in from this domain will be required to sign in via SSO.

Once we've received this information from you, We'll setup SSO for you and let you know once it's ready to be used.

:::warning
For security purposes, existing [Applications](https://reference.airbyte.com/reference/authentication) used to access the Airbyte API that were created before enabling SSO **will be disabled** once the user that owns the Application signs in via SSO for the first time. After enabling SSO, please make sure to replace any Application secrets that were previously in use.
:::

## Self-Managed Enterprise

To set up single sign on for Airbyte Self-Managed Enterprise, complete the following steps.

- [Create an Entra ID application for Airbyte](#sme-entra-id-app)
- [Create client credentials](#sme-credentials)
- [Update Airbyte's values.yaml file](#sme-update-values)
- [Redeploy Airbyte](#sme-deploy)

### Create application {#sme-entra-id-app}

To start, you create a new Entra ID application for Airbyte.

1. Log into the [Azure Portal](https://portal.azure.com/), search for the Entra ID service, and go to the Entra ID overview page.

2. Click **Add** > **App registration**.

3. Fill out the Register an application form.

    - **Name**: Enter a descriptive integration name.

    - **Supported account types**: Choose "Accounts in this organizational directory only" unless you have a reason to choose a different one.

    - **Redirect URI**: Choose **Single-page application (SPA)** and enter the domain depends of your Airbyte installation location, but the URI should look similar to `https://airbyte.example.com?checkLicense=true`.

4. Click **Register**. You are taken to your application's overview page.

5. Click **Endpoints**.

6. Copy the URL for **OpenID Connect metadata document** and open it in a new tab. You need some of these values later, so set it aside for a moment.

### Create client credentials {#sme-credentials}

You need to complete several steps to properly authenticate.

#### Expose an API

1. Click **Manage** > **Expose an API** > **Add a scope**.

2. Click **Save and continue**.

3. Fill out the form.

    - **Who can consent?**: Set to **Admins and users**.

    - **Admin content display name**: Provide a name like "Airbyte access".

    - **Admin content description**: Provide a description like "Allow access to Airbyte".

    - **State**: Enabled.

    - Set other fields as you like.

4. Click **Add scope**.

5. Click **Add a client application**. Fill out the form to link your client application and your scope.

#### Make yourself an owner

1. Click **Manage** > **Owners** > **Add owners**.

2. Add yourself as an owner and click **Select**.

#### Grant API permissions

1. Click **Manage** > **API permissions** > **Add a permission**

2. Click **My APIs**.

3. Click your Airbyte application.

4. Grant your "Airbyte access" permission you created earlier.

5. **Delete** any **Microsoft Graph** permissions.

### Update Airbyte's values.yaml file {#sme-update-values}

Once you have an app integration for Airbyte, update the values.yaml file you use when you deploy Airbyte. This section is where you need information from the well-known endpoint you opened earlier.

Under `global`, add a new `auth` section and fill in the following data.

```yaml title="values.yaml"
global: 

  edition: "enterprise"
  airbyteUrl: "airbyte.example.com"

  enterprise:
    secretName: "airbyte-license"
    licenseKeySecretKey: "LICENSE_KEY"

  # Add this new auth section. See below for help populating these values.
  auth:
    identityProvider: 
      type: generic-oidc
      generic-oidc: 
        clientId: YOUR_CLIENT_ID
        audience: YOUR_AUDIENCE
        issuer: YOUR_ISSUER
        endpoints: 
          authorizationServerEndpoint: YOUR_AUTH_ENDPOINT
          jwksEndpoint: YOUR_JWKS_ENDPOINT
```

You collect these values from Microsoft in the locations shown below.

- `clientId`: In Entra ID, on your application page, use the **Application (client) ID**.

- `audience`: Same as `clientId`.

- `issuer`: In your well-known endpoint, use `issuer`.

- `authorizationServerEndpoint`: Same as `issuer`.

- `jwksEndpoint`: In your well-known endpoint, use `jwks_uri`.

### Redeploy Airbyte {#sme-deploy}

In your command-line tool, deploy Airbyte using your updated values file. The examples here may not reflect your actual Airbyte version and namespace conventions, so make sure you use the settings that are appropriate for your environment.

```bash title="Example using the default namespace in your cluster"
helm upgrade --install airbyte-enterprise airbyte/airbyte --version 1.6.0 --values values.yaml
```

```bash title="Example using or creating a namespace called 'airbyte'"
helm upgrade --install airbyte-enterprise airbyte/airbyte --version 1.6.0 -n airbyte --create-namespace --values values.yaml
```

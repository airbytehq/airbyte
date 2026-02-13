---
sidebar_label: Entra ID
products: cloud, oss-enterprise
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Set up single sign on using Entra ID

This guide shows you how to set up Microsoft Entra ID (formerly Azure ActiveDirectory) and Airbyte so your users can log into Airbyte using your organization's identity provider (IdP) and OpenID Connect (OIDC).

## Overview

This guide is for administrators. It assumes you have:

- Basic knowledge of Entra ID, OIDC, and Airbyte
- The permissions to manage Entra ID in your organization
- Organization admin permissions for Airbyte

The exact process differs between the Cloud or Self-Managed versions of Airbyte. Steps for both are below.

## Cloud with Entra ID OIDC

:::warning
For security purposes, Airbyte disables existing [applications](/platform/enterprise-setup/api-access-config) used to access the Airbyte API once the user who owns the application signs in with SSO for the first time. Replace any Application secrets that were previously in use to ensure your integrations don't break.
:::

### Part 1: Create an application in Entra ID

Create a new [Entra ID application](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/what-is-application-management).

1. Log into the [Azure Portal](https://portal.azure.com/) and search for the Entra ID service.

2. From the Entra ID overview page, click **Add** > **App registration** at the top of the screen.

3. Specify any name you want (for example, "Airbyte").

4. Configure a **Redirect URI** with the type **Web** and the following value: `https://cloud.airbyte.com/auth/realms/<your-company-identifier>/broker/default/endpoint`

    Replace `<your-company-identifier>` with a unique identifier for your organization. This is often your organization name or domain. For example, `airbyte`. You'll use this same identifier when configuring SSO in Airbyte.

    :::tip
    To avoid coming back later to change this, check if this company identifier is available now by trying to log into Airbyte with it. If the company identifier is already claimed, Airbyte tries and fails to log you into another organization's IdP.
    :::

5. Click **Register** to create the application.

### Part 2: Create client credentials in Entra ID

Create client credentials so Airbyte can talk to your application.

1. On your application details page, click **Certificates & Secrets**.

2. Click the **Client secrets** tab.

3. Click **New client secret**. Specify any description you want and any expiry date you want.

    :::tip
    Choose an expiry date at least 12 months in the future, if you can. When a client secret expires, you need to give Airbyte the new one or people won't be able to log in.
    :::

4. Copy the **Value** (the client secret itself) immediately after you create it. You won't be able to view this later.

### Part 3: Domain verification

Before you can enable SSO, you must prove to Airbyte that you or your organization own the domain on which you want to enable SSO. You can enable as many domains as you need.

1. In Airbyte, click **Organization settings** > **SSO**.

2. Click **Add Domain**.

3. Enter your domain name (`example.com`, `airbyte.com`, etc.) and click **Add Domain**. The domain is added to the Domain Verification list with a "Pending" status and Airbyte shows you the necessary DNS record.

4. Add the DNS record to your domain. You might need help from your IT team to do this. Generally, you follow a process like this:

    1. Sign into the website where you manage your domain.

    2. Look for something like **DNS Records**, **Domain Management**, or **Name Server Management**. Click it to go to your domain's DNS settings.

    3. Find TXT records.

    4. Add a new TXT record using the record type, record name, and record value that Airbyte gave you.

    5. Save the new TXT record.

5. Wait for Airbyte to verify the domain. This process can take up to 24 hours, but typically it happens faster. If nothing has happened after 24 hours, verify that you entered the TXT record correctly.

### Part 4: Configure and test SSO in Airbyte

1. In Airbyte, click **Organization settings** > **SSO**.

2. Click **Set up SSO**, then input the following information.

    - **Company identifier**: The unique identifier you used in the redirect URI in Entra ID. For example, `airbyte`.

    - **Client ID**: The client ID you created in the preceding section. Find this in the Essentials section of your Entra ID application's homepage.

    - **Client secret**: The client secret you created in the preceding section.

    - **Discovery URL**: Your OpenID Connect metadata endpoint. The format is similar to `https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration`.

3. Click **Test your connection** to verify your settings. Airbyte forwards you to your identity provider. Log in to test that your credentials work.

    - If the test is successful, you return to Airbyte and see a "Test Successful" message.

    - If the test wasn't successful, either Airbyte or Entra ID show you an error message, depending on what the problem is. Verify the values you entered and try again.

4. Click **Activate**.

Once you activate SSO, users with your email domain must sign in using SSO.

#### If users can't log in

If you successfully set up SSO but your users can't log into Airbyte, verify that they have access to the Airbyte application you created in Entra ID.

### Update SSO credentials

To update SSO for your organization, [contact support](https://support.airbyte.com).

### Domain verification statuses

Airbyte shows one of the following statuses for each domain you add:

**Pending**: Airbyte created the DNS record details and is waiting to find the record in DNS. You see this status after you add a domain. DNS propagation can take time. If the status is still Pending after 24 hours, verify that the record name and value exactly match what Airbyte shows.

**Verified**: Airbyte found a TXT record with the expected value. The domain is verified and can be used with SSO. Users with email addresses on this domain must sign in with SSO.

**Failed**: Airbyte found a TXT record at the expected name, but the value doesn't match. This usually means the TXT record was created with a typo or wrong value. Update the TXT record to match the value shown in Airbyte, then click **Reset** to retry verification.

**Expired**: Airbyte couldn't verify the domain within 14 days, so it marked the verification as expired. After you've fixed your DNS configuration, click **Reset** to move it back to Pending, or delete it and start over.

### Remove a domain from SSO

If you no longer need a domain for SSO purposes, delete its verification.

1. In Airbyte, click **Organization settings** > **SSO**.

2. Next to the domain you want to stop using, click **Delete**.

<!-- Organization admins can log in using your email and password (instead of SSO) to update SSO settings. If your client secret expires or you need to update your SSO configuration, follow these steps.

1. In Airbyte, click **Organization settings** > **General**.

2. Click **Set up SSO** > **Re-test your connection**.

3. Update the form fields as needed.

4. Click **Test your connection** to verify the updated credentials work correctly.

5. Click **Activate SSO**. -->

## Self-Managed Enterprise with Entra ID OIDC

### Create application

You need to create a new Entra ID application for Airbyte. Log into the [Azure Portal](https://portal.azure.com/) and search for the Entra ID service.

From the overview page of Entra ID, press **Add** > **App registration** on the top of the screen. The name you select is your app integration name. Once chosen, **choose who can use the application, typically set to "Accounts in this organization directory only" for specific access,** and configure a **Redirect URI** of type **Web** with the following value:

```text
<your-airbyte-domain>/auth/realms/airbyte/broker/<app-integration-name>/endpoint
```

Hit **Register** to create the application.

### Create client credentials

To create client credentials for Airbyte to interface with your application, head to **Certificates & Secrets** on the detail screen of your application and select the **Client secrets** tab. Then:

1. Click **New client secret**, and enter the expiry date of your choosing. You'll need to pass in the new client secret every time the old one expires to continue being able to log in via Entra ID.
2. Copy the **Value** (the client secret itself) immediately after creation. You won't be able to view this later on.

:::caution
Depending on the default "Admin consent require' value for your organization you may need to manually provide Admin consent within the **API Permissions** menu. To do so click **API Permissions** and then click **Grant admin consent for Airbtyte** (see image below.)
:::

<img width="928" alt="Admin Consent Option" src="https://github.com/airbytehq/airbyte/assets/156025126/30818c10-de4f-4411-ba1d-8d82b74326fd" />

### Setup information needed

Once your Microsoft Entra ID app is set up, you're ready to deploy Airbyte Self-Managed Enterprise with SSO. Take note of the following configuration values, as you will need them to configure Airbyte to use your new SSO app integration:

    * OpenID Connect metadata document: You'll find this in the list of endpoints found in the **Endpoints** panel, which you can open from the top bar of the **Overview** page. This will be used to populate the `Domain` field in your `values.yaml`.
    * App Integration Name: The name of the Entra ID application created in the first step.
    * Client ID: You'll find this in the **Essentials** section on the **Overview** page of the application you created.
    * Client Secret: The client secret you copied in the previous step.

Use this information to configure the auth details of your `values.yaml` for your Self-Managed Enterprise deployment. To learn more on deploying Self-Managed Enterprise, see the [implementation guide](/platform/enterprise-setup/implementation-guide).

## Self-Managed Enterprise with Entra ID Generic OIDC

To set up single sign on for Airbyte Self-Managed Enterprise, complete the following steps.

- [Create an Entra ID application for Airbyte](#sme-entra-id-app)
- [Create client credentials](#sme-credentials)
- [Update Airbyte's values.yaml file](#sme-update-values)
- [Redeploy Airbyte](#sme-deploy)

:::note
You can only use generic OIDC after you migrate to Helm chart V2.
<!-- [Helm chart V2](../../enterprise-setup/chart-v2-enterprise). -->
:::

### Create application {#sme-entra-id-app}

To start, you create a new Entra ID application for Airbyte.

1. Log into the [Azure Portal](https://portal.azure.com/), search for the Entra ID service, and go to the Entra ID overview page.

2. Click **Add** > **App registration**.

3. Fill out the Register an application form.

    - **Name**: Enter a descriptive integration name.

    - **Supported account types**: Choose "Accounts in this organizational directory only" unless you have a reason to choose a different one.

    - **Redirect URI**: Choose **Single-page application (SPA)** and enter the domain depends of your Airbyte installation location, but the URI should look similar to `https://airbyte.example.com`.

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
      genericOidc: 
        clientId: YOUR_CLIENT_ID
        audience: YOUR_AUDIENCE
        extraScopes: YOUR_EXTRA_SCOPES
        issuer: YOUR_ISSUER
        endpoints: 
          authorizationServerEndpoint: YOUR_AUTH_ENDPOINT
          jwksEndpoint: YOUR_JWKS_ENDPOINT
```

You collect these values from Microsoft in the locations shown below.

- `clientId`: In Entra ID, on your application page, use the **Application (client) ID**.

- `audience`: Same as `clientId`.

- `extraScopes`: If you've defined extra scopes in your app registration, you can reference them here. Extra scopes are included in the authorization code flow and are sometimes required to provide web apps like Airbyte with valid JSON web tokens. In the Azure portal, **Entra ID** > **App registrations** > your app > **Expose an API**.  The format looks like `api://12345678-90ab-cdef-1234-567890abcdef/<SCOPE_NAME>`. Microsoft Graph API scopes and optional claims aren't supported.

- `issuer`: In your well-known endpoint, use `issuer`.

- `authorizationServerEndpoint`: Same as `issuer`.

- `jwksEndpoint`: In your well-known endpoint, use `jwks_uri`.

### Redeploy Airbyte {#sme-deploy}

In your command-line tool, deploy Airbyte using your updated values file.

```bash
helm upgrade airbyte-enterprise airbyte-v2/airbyte \
  --namespace airbyte-v2 \       # Target Kubernetes namespace
  --values ./values.yaml \       # Custom configuration values
  --version 2.x.x                # Helm chart version to use
```

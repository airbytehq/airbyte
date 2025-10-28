---
sidebar_label: Okta
products: oss-enterprise, cloud-teams
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Set up single sign on using Okta

This guide shows you how to set up Okta and Airbyte so your users can log into Airbyte using your organization's identity provider (IdP).

## Overview

This guide is for administrators. It assumes you have:

- Basic knowledge of Okta, OpenID Connect (OIDC), and Airbyte
- The permissions to manage Okta in your organization
- Organization admin permissions for Airbyte

The exact process differs between the Cloud or Self-Managed versions of Airbyte. Steps for both are below.

## Cloud with Okta OIDC

:::warning
For security purposes, when a user who owns [applications](/platform/enterprise-setup/api-access-config) logs in with SSO for the first time, Airbyte disables their existing applications. Those users must replace any application secrets that were previously in use to ensure API and Terraform integrations don't break.
:::

### Part 1: Create a new Okta application

1. In Okta, create a new Okta OIDC App Integration for Airbyte. For help, see [Okta's documentation](https://help.okta.com/en-us/content/topics/apps/apps_app_integration_wizard_oidc.htm). Create an app integration with the following options.

    - **Sign-in method**: OIDC - OpenID Connect

    - **Application type**: Web application

      ![Screenshot of Okta app integration creation modal](./assets/okta-create-new-app-integration.png)

2. Click **Next**.

3. Set the following parameters for your app integration.

    - **App integration name**: `Airbyte` (or something similar)

    - **Grant type**: `Authorization code`

    - **Sign-in redirect URIs**: `https://cloud.airbyte.com/auth/realms/<your-company-identifier>/broker/default/endpoint`

        Replace `<your-company-identifier>` with a unique identifier for your organization. This is often your organization name or domain (for example, `airbyte`). You'll use this same identifier when configuring SSO in Airbyte.

        :::tip
        To avoid coming back later to change this, check if this company identifier is available now by trying to log into Airbyte with it. If the company identifier is already claimed, Airbyte tries and fails to log you into another organization's IdP.
        :::

    - **Sign-out redirect URIs**: `https://cloud.airbyte.com/auth/realms/<your-company-identifier>/broker/default/endpoint/logout_response`

    - **Trusted origins**: Leave empty.

    - **Assignments > Controlled access**: Depending on your needs, choose either `Limit access to selected groups` or `Allow everyone in your organization to access`.

    - Leave other values as defaults unless you have a reason to change them.

4. Click **Save**.

### Part 2: Configure and test SSO in Airbyte

1. In Airbyte, click **Organization settings** > **General**.

2. Click **Set up SSO**, then input the following information.

    - **Company identifier**: The unique identifier you used in the redirect URI in Okta. For example, `airbyte`.

    - **Client ID**: In Okta's administrator panel, **Applications** > **Applications** > **Airbyte** > **General** tab > **Client ID**.

    - **Client secret**: Your client secret from your Okta application.

    - **Discovery URL**: Your OpenID Connect (OIDC) metadata endpoint. It's similar to `https://<yourOktaDomain>/.well-known/openid-configuration`.

3. Click **Test your connection** to verify your settings. Airbyte forwards you to your identity provider. Log in to test that your credentials work.

    - If the test is successful, you return to Airbyte and see a "Test Successful" message.

    - If the test wasn't successful, either Airbyte or Okta show you an error message, depending on what the problem is. Verify the values you entered and try again.

4. Enter your **Email domain** (for example, `airbyte.io`) and click **Activate SSO**.

    :::note Limitations and restrictions on domains
    - If you use multiple email domains, only enter one domain here. After activation, [contact support](https://support.airbyte.com) to have them add additional domains for you.
    - You can't claim an email domain if someone using that domain exists in another organization. For example, if your email domain is `example.com`, but someone with an `example.com` email uses Airbyte for another organization, you can't enable SSO for that domain. This also means SSO is unavailable for common public email domains like `gmail.com`.
    :::

Once you activate SSO, users with your email domain must sign in using SSO.

#### If users can't log in

If you successfully set up SSO but your users can't log into Airbyte, verify that they have access to the Airbyte application you created in Okta.

### Update SSO credentials

To update SSO for your organization, [contact support](https://support.airbyte.com).

<!-- Organization admins can log in using your email and password (instead of SSO) to update SSO settings. If your client secret expires or you need to update your SSO configuration, follow these steps.

1. In Airbyte, click **Organization settings** > **General**.

2. Click **Set up SSO** > **Re-test your connection**.

3. Update the form fields as needed.

4. Click **Test your connection** to verify the updated credentials work correctly.

5. Click **Activate SSO**. -->

#### Delete SSO configuration

To remove SSO from your organization, contact Airbyte's [support team](https://support.airbyte.com).

## Self-Managed Enterprise with Okta OIDC

You need to create a new Okta OIDC App Integration for Airbyte. Documentation on how to do this in Okta can be found [here](https://help.okta.com/en-us/content/topics/apps/apps_app_integration_wizard_oidc.htm). You should create an app integration with **OIDC - OpenID Connect** as the sign-in method and **Web Application** as the application type:

![Screenshot of Okta app integration creation modal](./assets/okta-create-new-app-integration.png)

Before you can proceed, you require your **Company Identifier** so you can properly fill in these values. Your contact at Airbyte gives this to you.

Create the application with the following parameters:

<dl>
  <dt>**App integration name**</dt>
  <dd>Please choose a URL-friendly app integration name without spaces or special characters, such as `my-airbyte-app`. Screenshot of Okta app integration name Spaces or special characters in this field could result in invalid redirect URIs.</dd>
  <dt>**Logo** (optional)</dt>
  <dd>You can upload an Airbyte logo, which you can find at https://airbyte.com/company/press</dd>
  <dt>**Grant type**</dt>
  <dd>Only **Authorization Code** should be selected</dd>
  <dt>**Sign-in redirect URIs**</dt>
  <dd>
  ```
  <your-airbyte-domain>/auth/realms/airbyte/broker/<app-integration-name>/endpoint
  ```

  `<your-airbyte-domain>` refers to the domain you access your Airbyte instance at, e.g. `https://airbyte.internal.mycompany.com`

  `<app-integration-name>` refers to the value you entered in the **App integration name** field
  </dd>
  <dt>**Sign-out redirect URIs**</dt>
  <dd>
  ```
  <your-airbyte-domain>/auth/realms/airbyte/broker/<app-integration-name>/endpoint/logout_response
  ```
  </dd>
  <dt>**Trusted Origins**</dt>
  <dd>Leave empty</dd>
  <dt>**Assignments > Controlled Access**</dt>
  <dd>You can control whether everyone in your Okta organization should be able to access Airbyte using their Okta account or limit it only to a subset of your users by selecting specific groups who should get access.</dd>
</dl>

Once your Okta app is set up, you're ready to deploy Airbyte with SSO. Take note of the following configuration values, as you will need them to configure Airbyte to use your new Okta SSO app integration:

* Okta domain ([How to find your Okta domain](https://developer.okta.com/docs/guides/find-your-domain/main/))
* App Integration Name
* Client ID
* Client Secret

Visit the [implementation guide](../../enterprise-setup/implementation-guide.md) for instructions on how to deploy Airbyte Enterprise using `kubernetes`, `kubectl` and `helm`.

## Self-Managed Enterprise with Okta Generic OIDC

To set up single sign using generic OIDC for Airbyte Self-Managed Enterprise, complete the following steps.

- [Create an Okta application for Airbyte](#sme-create-okta-app)
- [Add an authorization server (optional)](#sme-auth-server)
- [Add a policy for Airbyte](#sme-policy)
- [Update Airbyte's values.yaml file](#sme-values)
- [Redeploy Airbyte](#sme-deploy)

:::note
You can only use generic OIDC after you migrate to Helm chart V2.
<!-- [Helm chart V2](../../enterprise-setup/chart-v2-enterprise). -->
:::

### Create an Okta app for Airbyte {#sme-create-okta-app}

Follow these steps to set up an Okta app integration for Airbyte. If you need more help setting up an app integration, see [Okta's documentation](https://help.okta.com/en-us/content/topics/apps/apps_app_integration_wizard_oidc.htm).

1. Log into your Okta administrator dashboard. For example: `example.okta.com/admin/dashboard`.

2. Click **Applications** > **Applications**.

3. Click **Create App Integration**, then choose the following values.

    - **Sign-in method**: OIDC - OpenID Connect

    - **Application type**: Single-Page Application

4. Click **Next**.

5. Choose the following options:

    - **App integration name**: Airbyte

    - **Grant type**: Authorization Code, Refresh Token

    - **Sign-in redirect URIs**: The domain depends of your Airbyte installation location, but the URI should look similar to `https://airbyte.example.com`.

    - **Sign-out redirect URIs**: Set it to your base Airbyte site. For example: `https://airbyte.example.com`.

    - **Controlled access**: Depending on your needs, choose either `Limit access to selected groups` or `Allow everyone in your organization to access`.

    - Leave other values as defaults unless you have a reason to change them.

6. Click **Save**. Okta takes you to your app page.

7. On the app page, make sure you have **Require PKCE as additional verification** enabled. Leave other values as defaults.

### Add an authorization server {#sme-auth-server}

You need an authorization server, but you probably already have one. If you do, you can use it for Airbyte too. If you need to create a new one, follow these steps.

1. Click **Security** > **API**.

2. Click **Add Authorization Server**.

3. Give your authorization server a name, audience, and description. Then, click **Save**. For demonstration purposes, this guide assumes you name your authorization server `webapps`.

:::tip
Before continuing, go to your authorization server's page in Okta and open the **Issuer Metadata URL** link in a new tab. This is your well-known endpoint. You need some of these values later, so set it aside for a moment.
:::

### Add an access policy {#sme-policy}

Add an access policy to your authorization server.

1. Click **Security** > **API** > choose your authorization server > **Access Policies** > **Add Policy**.

2. Give your policy a name and description. Under **Assign to**, choose **The following clients**, then search for your Airbyte application (you probably called it Airbyte). Okta shows you your new policy.

3. Click **Create Policy**.

4. Click **Add rule**.

5. Fill out the form.

    - Give your rule a descriptive name, like "Log into Airbyte".

    - Grant **Authorization Code** and **Token exchange**. Don't grant anything else unless you have a reason to.

    - Choose **Any user assigned the app**.

    - Choose **Any scopes**.

    - Click **Create rule**.

    - Leave other values as defaults unless you have a reason to change them.

### Update your values.yaml file {#sme-values}

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

You collect these values from Okta in the locations shown below.

- `clientId`: In Okta's administrator panel, **Applications** > **Applications** > **Airbyte** > **General** tab > **Client ID**.

- `audience`: In Okta's administrator panel, **Security** > **API** > **Authorization Servers** tab > **Audience**. Choose the audience for the authorization server you're using with Airbyte.

- `extraScopes`: If you've defined extra scopes in your authorization server, you can reference them here. Extra scopes are included in the authorization code flow and are sometimes required to provide web apps like Airbyte with valid JSON web tokens. In Okta's administrator panel, **Security** > **API** > **Authorization Servers** tab > your authorization server > **Scopes**.

- `issuer`: In your well-known endpoint, use the `issuer`.

- `authorizationServerEndpoint`: In your well-known endpoint, use the `authorization_endpoint`, but omit the `/v1/authorize` portion. For example, `https://example.okta.com/oauth2/default/`.

- `jwksEndpoint`: In your well-known endpoint, use the `jwks_uri`.

### Deploy Airbyte {#sme-deploy}

In your command-line tool, deploy Airbyte using your updated values file. The examples here may not reflect your actual Airbyte version and namespace conventions, so make sure you use the settings that are appropriate for your environment.

```bash title="Example using a namespace called 'airbyte'"
helm upgrade -i \
--namespace airbyte \
--values ./values.yaml \
airbyte \
airbyte-v2/airbyte \
--version 2.x.x
```

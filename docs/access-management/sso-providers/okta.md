---
sidebar_label: Okta
products: oss-enterprise, cloud-teams
---

# Set up single sign on using Okta

This guide shows you how to set up Okta and Airbyte so your users can log into Airbyte using your organization's identity provider (IdP) using OpenID Connect (OIDC). 

## Overview

This guide is for administrators. It assumes you have:

- Basic knowledge of Okta, OIDC, and Airbyte
- The permissions to manage Okta in your organization
- The permissions to manage Airbyte in your organization

The exact process differs between the Cloud or Self-Managed versions of Airbyte. Steps for both are below.

## Cloud with Teams add-on

:::warning
For security purposes, Airbyte disables existing [applications](/enterprise-setup/api-access-config) used to access the Airbyte API once the user who owns the application signs in with SSO for the first time. Replace any Application secrets that were previously in use to ensure your integrations don't break.
:::

Before you can proceed, you require your **Company Identifier** so you can properly fill in these values. Your contact at Airbyte gives this to you.

1. Create the application with the following parameters:

    <dl>
      <dt>**App integration name**</dt>
      <dd>A human readable name for the application (e.g. **Airbyte Cloud**). This is only used for identification inside your Okta dashboard.</dd>
      <dt>**Logo** (optional)</dt>
      <dd>You can upload an Airbyte logo, which you can find at https://airbyte.com/company/press</dd>
      <dt>**Grant type**</dt>
      <dd>Only select **Authorization Code**.</dd>
      <dt>**Sign-in redirect URIs**</dt>
      <dd>
      ```
      https://cloud.airbyte.com/auth/realms/<your-company-identifier>/broker/default/endpoint
      ```
      </dd>
      <dt>**Sign-out redirect URIs**</dt>
      <dd>
      ```
      https://cloud.airbyte.com/auth/realms/<your-company-identifier>/broker/default/endpoint/logout_response
      ```
      </dd>
      <dt>**Trusted Origins**</dt>
      <dd>Leave empty.</dd>
      <dt>**Assignments > Controlled Access**</dt>
      <dd>You can control whether everyone in your Okta organization should be able to access Airbyte using their Okta account or limit it only to a subset of your users by selecting specific groups who should get access.</dd>
    </dl>

2. Give your Airbyte contact the following information of the created application.

    - Your **Okta domain** (it's not specific to this application, see [Find your Okta domain](https://developer.okta.com/docs/guides/find-your-domain/main/))
    - **Client ID**
    - **Client Secret**
    - **Email Domain** (users signing in from this domain are required to sign in via SSO)

3. Your contact at Airbyte sets up SSO for you and lets you know once it's ready.

## Self-Managed Enterprise

To set up single sign on for Airbyte Self-Managed Enterprise, complete the following steps.

- [Create an Okta application for Airbyte](#sme-create-okta-app)
- [Add an authorization server (optional)](#sme-auth-server)
- [Add a policy for Airbyte](#sme-policy)
- [Update Airbyte's values.yaml file](#sme-values)
- [Redeploy Airbyte](#sme-deploy)

### Create an Okta app for Airbyte {#sme-create-okta-app}

Follow these steps to set up an Okta app integration for Airbyte. If you need more help setting up an app integration, see [Okta's documentation](https://help.okta.com/en-us/content/topics/apps/apps_app_integration_wizard_oidc.htm).

1. Log into your Okta administrator dashboar. For example: `example.okta.com/admin/dashboard`.

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
      generic-oidc: 
        clientId: YOUR_CLIENT_ID
        audience: YOUR_AUDIENCE
        issuer: YOUR_ISSUER
        endpoints: 
          authorizationServerEndpoint: YOUR_AUTH_ENDPOINT
          jwksEndpoint: YOUR_JWKS_ENDPOINT
```

You collect these values from Okta in the locations shown below.

- `clientId`: In Okta's administrator panel, **Applications** > **Applications** > **Airbyte** > **General** tab > **Client ID**.

- `audience`: In Okta's administrator panel, **Security** > **API** > **Authorization Servers** tab > **Audience**. Choose the audience for the authorization server you're using with Airbyte.

- `issuer`: In your well-known endpoint, use the `issuer`.

- `authorizationServerEndpoint`: In your well-known endpoint, use the `authorization_endpoint`, but omit the `/v1/authorize` portion. For example, `https://example.okta.com/oauth2/default/`.

- `jwksEndpoint`: In your well-known endpoint, use the `jwks_uri`.

### Deploy Airbyte {#sme-deploy}

In your command-line tool, deploy Airbyte using your updated values file. The examples here may not reflect your actual Airbyte version and namespace conventions, so make sure you use the settings that are appropriate for your environment.

```bash title="Example using the default namespace in your cluster"
helm upgrade --install airbyte-enterprise airbyte/airbyte --version 1.6.0 --values values.yaml
```

```bash title="Example using or creating a namespace called 'airbyte'"
helm upgrade --install airbyte-enterprise airbyte/airbyte --version 1.6.0 -n airbyte --create-namespace --values values.yaml
```

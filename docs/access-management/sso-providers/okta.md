---
sidebar_label: Okta
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Setup Single Sign-On via Okta

This page guides you through setting up Okta for [Single Sign-On](../sso.md) with Airbyte.

Airbyte will communicate with your Okta account using OpenID Connect (OIDC).

## Creating an Okta app for Airbyte

:::info
The following steps need to be executed by an administrator of your company's Okta account.
:::

You will need to create a new Okta OIDC App Integration for your Airbyte. Documentation on how to do this in Okta can be found [here](https://help.okta.com/en-us/content/topics/apps/apps_app_integration_wizard_oidc.htm).

You should create an app integration with **OIDC - OpenID Connect** as the sign-in method and **Web Application** as the application type:

![Screenshot of Okta app integration creation modal](./assets/okta-create-new-app-integration.png)

On the following screen you'll need to configure all parameters for your Okta application:

<Tabs>
  <TabItem value="cloud" label="Cloud">
    You'll require to know your **Company Identifier** to fill in those values. You receive this
    from your contact at Airbyte.

    Create the application with the following parameters:

    <dl>
      <dt>**App integration name**</dt>
      <dd>A human readable name for the application (e.g. **Airbyte Cloud**). This is only used for identification inside your Okta dashboard.</dd>
      <dt>**Logo** (optional)</dt>
      <dd>You can upload an Airbyte logo, which you can find at https://airbyte.com/company/press</dd>
      <dt>**Grant type**</dt>
      <dd>Only **Authorization Code** should be selected</dd>
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
      <dd>Leave empty</dd>
      <dt>**Assignments > Controlled Access**</dt>
      <dd>You can control whether everyone in your Okta organization should be able to access Airbyte using their Okta account or limit it only to a subset of your users by selecting specific groups who should get access.</dd>
    </dl>
  </TabItem>
  <TabItem value="self-managed" label="Self Hosted">
    test this
  </TabItem>
</Tabs>

---
sidebar_label: Okta
products: cloud-teams
---

# Set up SCIM using Okta

Okta doesn't support adding SCIM provisioning to a custom OIDC app integration. Use your existing OIDC app for SSO and create a second, provisioning-only app for SCIM. For more information about this requirement, see [Okta's support article about configuring SCIM for a custom OIDC app](https://support.okta.com/help/s/article/configure-scim-for-a-custom-oidc-app). For SSO setup, see [Set up single sign on using Okta](../sso-providers/okta).

## Before you start

You need:

- Organization admin permissions in Airbyte.
- Administrator permissions in Okta.
- [SCIM enabled for your Airbyte organization](../scim#enable-scim-in-airbyte).
- A [verified email domain in Airbyte](../sso-providers/okta#part-2-domain-verification) for every domain you plan to provision.

Before you configure Okta, [enable SCIM in Airbyte](../scim#enable-scim-in-airbyte) and copy the SCIM base URL and bearer token.

## Create the provisioning-only app

In Okta, create a second app integration for SCIM. Keep your existing OIDC app for SSO; the SCIM app doesn't need to provide working SSO.

1. In the Okta Admin Console, go to **Applications** > **Applications** and click **Browse App Catalog**.

2. Search for `SCIM 2.0`, select **SCIM 2.0 Test App (Header Auth)**, and click **Add Integration**.

3. Name the app, for example, `Airbyte SCIM`. You can hide the app from users because it is only used for provisioning.

4. Under **Sign-On Options**, select **SWA**. This app is never used for sign-in, because SCIM authenticates with the bearer token and SSO stays on your OIDC app. **SWA** just avoids configuring SAML settings that Airbyte can't use.

5. Click **Done**.

For Okta's current application flow, see Okta's [SCIM provisioning documentation](https://help.okta.com/oie/en-us/content/topics/apps/apps_app_integration_wizard_scim.htm) and [Configure provisioning for an app integration](https://help.okta.com/oie/en-us/content/topics/provisioning/lcm/lcm-provision-application.htm).

## Configure the API integration

On the new app, open the **Provisioning** tab and configure the API integration.

1. Click **Configure API Integration**.

2. Select **Enable API integration**.

3. Set **Base URL** to the **SCIM base URL** shown in Airbyte.

4. Set **API Token** to the Airbyte **Bearer token**.

5. Click **Test API Credentials**, then click **Save**.

If Okta offers password synchronization for the application, turn it off. Airbyte ignores passwords sent through SCIM.

:::note
If **Test API Credentials** returns `401` when you enter the bearer token as-is, try prefixing the value with `Bearer `. Airbyte expects the `Authorization: Bearer <token>` header.
:::

## Review attribute mappings

Before you assign people to the app, open the **Mappings** tab and remove mappings for attributes Airbyte doesn't accept. See [Supported user attributes](../scim#supported-user-attributes). An unsupported mapping causes provisioning to fail for the user, not just that field.

## Assign people to the app

Assign the people who should access Airbyte on the **Assignments** tab. You can assign people individually or assign an Okta group. Assignment triggers provisioning: enabling **Create Users** alone doesn't provision anyone.

An assigned, active user becomes an organization member in Airbyte.

## Enable provisioning actions

After you assign people to the app:

1. Open the **Provisioning** tab and, under **To App**, click **Edit**.

2. Enable the actions you need: **Create Users**, **Update User Attributes**, and **Deactivate Users**.

3. Save your changes.

## Push groups

Assigning an Okta group to the app provisions its members as users, but it doesn't create the group in Airbyte. To create a group in Airbyte, use Okta's **Push Groups** workflow.

Okta owns the group name and membership after provisioning. Airbyte owns permissions assigned to the group. Group members must be users provisioned into the same Airbyte organization. For group behavior and permissions, see [User groups](../user-groups).

## Deactivate and delete users

Use Okta deactivation to remove a user's organization access through SCIM; Airbyte also accepts SCIM `DELETE /Users/{id}`, but that is a protocol operation rather than a button in Okta.

When a user is deactivated, Airbyte removes their organization permissions, workspace permissions, and group memberships in that organization. Reactivating the user restores only baseline organization-member access. Your IdP must provision group membership again.

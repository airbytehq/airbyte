---
sidebar_label: Okta
products: cloud-teams
---

# Set up SCIM using Okta

Okta doesn't support adding SCIM provisioning to an OIDC app integration. Use your existing OIDC app for SSO and create a second, provisioning-only custom SWA app for SCIM. For more information, see Okta's [SCIM provisioning documentation](https://help.okta.com/oie/en-us/content/topics/apps/apps_app_integration_wizard_scim.htm). For SSO setup, see [Set up single sign on using Okta](../sso-providers/okta).

## Before you start

You need:

- Organization admin permissions in Airbyte.
- Administrator permissions in Okta.
- Provisioning enabled for your Okta organization. If **SCIM** doesn't appear in the **Provisioning** field on your app's settings page, contact Okta Support to activate the feature.
- [SCIM enabled for your Airbyte organization](../scim#enable-scim-in-airbyte).
- A [verified email domain in Airbyte](../sso-providers/okta#part-2-domain-verification) for every domain you plan to provision.

Before you configure Okta, [enable SCIM in Airbyte](../scim#enable-scim-in-airbyte) and copy the SCIM base URL and bearer token.

## Create the provisioning-only app

In Okta, create a second custom app integration for SCIM. Keep your existing OIDC app for SSO; this app is used only for provisioning.

1. In the Okta Admin Console, go to **Applications** > **Applications** and click **Create App Integration**.

2. Select **SWA - Secure Web Authentication** as the sign-on method, then click **Next**.

3. Under **General App Settings**, configure the app:

   - Set **App name** to a name such as `Airbyte SCIM`.
   - Set **App's login page URL** to your Airbyte URL. This app is never used for sign-in, so the value only needs to be a valid URL.
   - Set **App visibility** to **Do not display application icon to users**. Users sign in through your separate OIDC app, so hiding this provisioning-only app avoids confusion in their Okta dashboard.
   - Under **App type**, select the option for an internal application.

4. Click **Finish**.

For details, see Okta's [SWA app integration documentation](https://help.okta.com/oie/en-us/content/topics/apps/apps_app_integration_wizard_swa.htm) and [SCIM provisioning documentation](https://help.okta.com/oie/en-us/content/topics/apps/apps_app_integration_wizard_scim.htm).

## Enable SCIM provisioning

On the new app, open the **General** tab and, under **App Settings**, click **Edit**.

1. Set **Provisioning** to **SCIM**.

2. Click **Save**.

## Configure the SCIM connection

On the new app, open the **Provisioning** tab and go to **Settings** > **Integration**. Click **Edit**.

1. Set **SCIM connector base URL** to the **SCIM base URL** shown in Airbyte.

2. Set the unique identifier field for users to `userName`.

3. Under **Supported provisioning actions**, select **Push New Users**, **Push Profile Updates**, and **Push Groups**. Leave **Import New Users and Profile Updates** off because Airbyte isn't a profile source for Okta.

4. Under **Authentication Mode**, select **HTTP Header**.

5. Enter the Airbyte bearer token by itself in the **Authorization** field. Okta adds the `Bearer ` prefix when it sends the header.

6. Click **Test API Credentials**, then click **Save**.

If Okta offers password synchronization for the application, turn it off. Airbyte ignores passwords sent through SCIM.

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

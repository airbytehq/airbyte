---
sidebar_label: Entra ID
products: cloud-teams
---

# Set up SCIM using Entra ID

This guide shows you how to configure SCIM provisioning with a custom, non-gallery Microsoft Entra enterprise application. It assumes that you already set up SSO with Entra ID. For SSO setup, see [Set up single sign on using Entra ID](../sso-providers/azure-entra-id).

This guide uses Airbyte's long-lived bearer token. Gallery applications and client-credentials or OAuth provisioning flows are out of scope.

## Before you start

You need:

- Organization admin permissions in Airbyte.
- Permission to manage enterprise applications in Entra ID.
- [SCIM enabled for your Airbyte organization](../scim#enable-scim-in-airbyte).
- A [verified email domain in Airbyte](../sso-providers/azure-entra-id#part-3-domain-verification) for every domain you plan to provision.

Before you configure Entra ID, [enable SCIM in Airbyte](../scim#enable-scim-in-airbyte) and copy the SCIM base URL and bearer token.

## Create or reuse an enterprise application

Create or reuse a custom, non-gallery enterprise application for Airbyte. See Microsoft's [automatic user provisioning documentation](https://learn.microsoft.com/en-us/entra/identity/app-provisioning/configure-automatic-user-provisioning-portal) for Entra's current application setup flow.

If you create a new application, use the application type that lets you configure automatic provisioning with a tenant URL and secret token.

## Configure automatic provisioning

1. In Entra ID, open the Airbyte enterprise application.

2. Open **Provisioning** and select **Automatic**.

3. Set **Tenant URL** to the **SCIM base URL** shown in Airbyte.

4. Set **Secret Token** to the Airbyte **Bearer token**.

5. Select **Test Connection**.

6. Save the provisioning configuration after the connection succeeds.

Airbyte shows the SCIM base URL after setup, but it shows the bearer token only during the enable or token-rotation flow.

## Review attribute mappings

Before you start provisioning, review the **Mappings** for users and groups. Entra ID's default mappings commonly include `addresses` and `phoneNumbers`, which Airbyte doesn't accept, so delete those mappings. Remove any other mappings for unsupported attributes. See [Supported user attributes](../scim#supported-user-attributes). An unsupported mapping causes provisioning to fail for the user, not just that field.

Airbyte does not support nested groups. Group members must be users that Entra ID provisions into the same Airbyte organization.

## Scope and start provisioning

Choose the users and groups that Entra ID should provision in the application's provisioning scope. Review the resulting users and groups in **Mappings**, then start provisioning.

Entra ID owns group names and membership. Airbyte owns permissions assigned to groups. For more information, see [User groups](../user-groups).

## Deactivate and delete users

Use Entra ID's provisioning state to deactivate a user when you want to remove their organization access through SCIM; Airbyte also accepts SCIM `DELETE /Users/{id}`, but that is a protocol operation rather than a button in Entra ID.

When a user is deactivated, Airbyte removes their organization permissions, workspace permissions, and group memberships in that organization. Reactivating the user restores only baseline organization-member access. Entra ID must provision group membership again.

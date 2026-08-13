---
sidebar_label: Entra ID
products: cloud-teams
title: Set up SCIM using Entra ID
---

# Set up SCIM using Entra ID

This guide shows you how to configure SCIM provisioning with a custom, non-gallery Microsoft Entra enterprise application. It assumes that you already set up SSO with Entra ID. For SSO setup, see [Set up single sign on using Entra ID](../sso-providers/azure-entra-id).

This guide uses Airbyte's long-lived bearer token. Gallery applications and client-credentials or OAuth provisioning flows are out of scope.

## Before you start

You need:

- Organization admin permissions in Airbyte.
- Permission to manage enterprise applications in Entra ID.
- SCIM enabled for your Airbyte organization.
- A verified email domain in Airbyte for every domain you plan to provision.

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

Before you start provisioning, review the **Mappings** for users and groups. Entra ID's default mappings can send attributes that Airbyte does not support. Airbyte returns `400` for unsupported attributes or invalid values.

Trim the mappings to the supported attributes listed in [SCIM provisioning](../scim#what-your-identity-provider-can-manage). In particular, make sure your mappings use:

- `userName`
- `externalId`, when you need it
- `active`
- `emails`
- Supported `name` fields
- `displayName` for groups
- `members` for groups

Airbyte does not support nested groups. Group members must be users that Entra ID provisions into the same Airbyte organization.

## Scope and start provisioning

Choose the users and groups that Entra ID should provision in the application's provisioning scope. Review the resulting users and groups in **Mappings**, then start provisioning.

Entra ID owns group names and membership. Airbyte owns permissions assigned to groups. For more information, see [User groups](../user-groups).

## Deactivate and delete users

Use Entra ID's provisioning state to deactivate a user when you want to remove their organization access through SCIM. Airbyte handles an actual SCIM `DELETE /Users/{id}` request independently of a provider-specific UI action.

When a user is deactivated, Airbyte removes their organization permissions, workspace permissions, and group memberships in that organization. Reactivating the user restores only baseline organization-member access. Entra ID must provision group membership again.

## Review against a live Entra ID tenant

Review the exact enterprise-application creation flow, **Provisioning** menu labels, **Mappings** controls, scoping controls, and start-provisioning action against a live Entra ID tenant. Microsoft can change these labels and the available application types.

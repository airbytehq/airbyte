---
sidebar_label: Okta
products: cloud-teams
---

# Set up SCIM using Okta

This guide shows you how to configure SCIM provisioning for the existing Airbyte Okta application. It assumes that you already set up SSO with Okta. For SSO setup, see [Set up single sign on using Okta](../sso-providers/okta).

## Before you start

You need:

- Organization admin permissions in Airbyte.
- Administrator permissions in Okta.
- SCIM enabled for your Airbyte organization.
- A verified email domain in Airbyte for every domain you plan to provision.

Before you configure Okta, [enable SCIM in Airbyte](../scim#enable-scim-in-airbyte) and copy the SCIM base URL and bearer token.

## Configure the Okta application

Use Okta's [SCIM provisioning documentation](https://help.okta.com/en-us/content/topics/provisioning/lcm/lcm-provisioning-scim-configure.htm) for the exact Okta UI labels and application navigation. The names can vary by Okta edition.

When you configure provisioning for the existing Airbyte application, use these values:

- **SCIM connector base URL**: The **SCIM base URL** from Airbyte.
- **Unique identifier field**: `userName`.
- **Authentication mode**: HTTP Header.
- **HTTP Header**: The Airbyte **Bearer token**.

Enable the provisioning capabilities that you need:

- Push new users.
- Push profile updates.
- Push groups.

If Okta offers password synchronization for the application, turn it off. Airbyte ignores passwords sent through SCIM.

## Test the connector

After you enter the base URL and bearer token, use Okta's connector test action to test the configuration. Resolve any connection or authentication errors before you enable provisioning.

## Enable user provisioning

When the connector test succeeds:

1. In Okta, open the Airbyte application's **Provisioning** settings.

2. Under **To App**, enable **Create users**, **Update users**, and **Deactivate users** as needed.

3. Assign the people who should access Airbyte to the application.

4. Save the provisioning settings.

Okta sends changes for the people assigned to the application. An assigned, active user becomes an organization member in Airbyte.

## Push groups

If you enabled **Push groups**, select the groups you want Okta to provision to Airbyte. Okta owns the group name and membership after provisioning. Airbyte owns permissions assigned to the group.

Group members must be users provisioned into the same Airbyte organization. For group behavior and permissions, see [User groups](../user-groups).

## Deactivate and delete users

Use Okta deactivation to remove a user's organization access through SCIM; Airbyte also accepts SCIM `DELETE /Users/{id}`, but that is a protocol operation rather than a button in Okta.

When a user is deactivated, Airbyte removes their organization permissions, workspace permissions, and group memberships in that organization. Reactivating the user restores only baseline organization-member access. Your IdP must provision group membership again.

<!-- Review against a live Okta tenant: confirm the exact Okta menu names, connector test location, provisioning capability labels, and group-push workflow against the Okta edition. This guide intentionally points to Okta's documentation instead of prescribing edition-specific navigation. -->

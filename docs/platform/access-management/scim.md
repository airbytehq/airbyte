---
products: cloud-teams
---

# SCIM provisioning

System for Cross-domain Identity Management (SCIM) lets your identity provider (IdP) create, update, and deactivate Airbyte users, and create [user groups](user-groups) and manage their membership, without an administrator doing that work in Airbyte.

SCIM is an add-on to [single sign on](sso). To use it, contact Airbyte to enable SCIM for your organization.

## How SCIM changes Airbyte

When SCIM is enabled, your IdP owns who belongs to your organization and which groups they're in. Airbyte still owns what those people and groups can do.

| Airbyte object                   | Owner when SCIM is enabled                                   |
| -------------------------------- | ------------------------------------------------------------ |
| Organization membership          | Your IdP                                                     |
| User profile details, like names | Your IdP                                                     |
| Group names                      | Your IdP                                                     |
| Group membership                 | Your IdP                                                     |
| Group permissions                | Airbyte, set by an organization admin                        |
| Individual user permissions      | Airbyte, set by an organization admin                        |

Because your IdP is the source of truth for membership, the **Members** page in Airbyte hides invitations while SCIM is enabled. To add or remove someone, assign or unassign them in your IdP.

Airbyte never receives passwords through SCIM. People still sign in with SSO.

## Before you start

You need the following:

- The Pro or Enterprise Flex plan, with SCIM enabled for your organization.
- Organization admin permissions in Airbyte.
- Permission to configure provisioning in Okta or Microsoft Entra ID.
- A **verified domain** in Airbyte for every email domain you plan to provision. Airbyte rejects any user whose email domain your organization hasn't verified. Add and verify domains in **Organization settings** > **SSO**. See the [Okta](sso-providers/okta) or [Entra ID](sso-providers/azure-entra-id) SSO guide for the DNS steps.

Set up SSO before SCIM. Users your IdP provisions can only sign in with the credentials your IdP manages.

## Enable SCIM in Airbyte

:::warning
Before you enable SCIM, review your existing Airbyte user groups and delete or rename any groups that your IdP should provision. Your IdP can't adopt an Airbyte group with the same name, so provisioning for that group keeps failing with a `409` response until you rename or delete the Airbyte group. After a group is created or adopted through SCIM, you can't rename it or change its membership in Airbyte while SCIM is enabled, and you can't delete it in Airbyte while its SCIM mapping exists, even after you disable SCIM. Groups that have never been mapped through SCIM remain editable and deletable in Airbyte.
:::

1. In Airbyte, click **Organization settings** > **SSO**.

2. In the SCIM section, choose your **Identity provider**: **Okta** or **Microsoft Entra ID**.

    :::warning
    You can't change the identity provider later. To switch providers, [contact support](https://support.airbyte.com).
    :::

3. Click **Enable SCIM**. Airbyte shows you a **SCIM base URL** and a **Bearer token**.

4. Copy both values. Airbyte shows the token only once. If you lose it, you must generate a new one.

    :::warning
    The bearer token grants your IdP the ability to create, modify, and deactivate users in your organization. Treat it like a password and store it in a secrets manager or password manager.
    :::

5. Paste the base URL and token into your IdP, then configure provisioning there. See [Set up SCIM using Okta](scim-providers/okta) or [Set up SCIM using Entra ID](scim-providers/azure-entra-id).

6. Come back to Airbyte and assign permissions to each group your IdP provisioned. Your IdP owns group names and membership, but only an organization admin can give a group permissions, and until you do, its members have organization member access and nothing more. See [User groups](user-groups).

Airbyte continues to display the base URL in the SCIM section after setup, but not the token.

## Manage the bearer token

The token doesn't expire, but you can replace it at any time.

1. Click **Organization settings** > **SSO**.

2. In the SCIM section, click **Generate new token**, then confirm.

The previous token stops working immediately, so your IdP can't provision anyone until you paste the new token into it. Like the first token, Airbyte shows the replacement only once.

## Disable and re-enable SCIM

Click **Disable SCIM** to stop your IdP from provisioning. Airbyte invalidates the token, and:

- Existing users, groups, and group memberships remain as they are.
- Group names and membership become editable in Airbyte again.
- SCIM-mapped groups remain undeletable in Airbyte while their mapping exists.
- Nobody loses access.

To resume provisioning, enable SCIM again with the same identity provider. Disabling SCIM doesn't reset that choice, so you can't switch identity providers yourself; contact Airbyte Support if you need to switch providers. Airbyte issues a new token, which you must paste into your IdP.

When you re-enable SCIM, Airbyte reconciles any users your IdP had already deactivated: those users lose their permissions and group memberships in this organization, the same way they would have if they were deactivated while SCIM was enabled.

## What your identity provider can manage

Airbyte implements SCIM 2.0 with the core `User` and `Group` schemas.

### Supported user attributes

Airbyte uses a strict allowlist for SCIM user attributes. If your IdP sends an attribute outside this list, Airbyte rejects the entire request with HTTP `400` and `scimType: invalidValue`. The `schemas` array must contain exactly the core User schema. Schema extensions, such as the enterprise user extension, cause the entire request to fail.

- `userName`, `externalId`, and `active`.
- `emails`: `value`, `type`, `primary`, and `display`.
- `name`: `formatted`, `givenName`, `familyName`, `middleName`, `honorificPrefix`, and `honorificSuffix`.
- `displayName`, `nickName`, `profileUrl`, `title`, `userType`, `preferredLanguage`, `locale`, and `timezone`.
- `id`, `meta`, `groups`, and `password` are accepted but ignored by Airbyte.

Each user needs a `userName` and at least one email. Provide no more than one primary email. If no primary email is provided, provide exactly one `work` email.

Users:

- Create, update, deactivate, reactivate, and delete users.
- Group membership is read-only on the user resource. Change membership on the group.

Groups:

- Create, rename, delete, and change membership.
- Supported group attributes are `displayName`, `externalId`, and `members`.
- Members must be active users that SCIM provisioned in the same organization.

Airbyte doesn't support the following:

- Assigning Airbyte permissions or roles through SCIM. An organization admin assigns permissions to groups in Airbyte. See [user groups](user-groups).
- Nested groups.
- Password synchronization. Airbyte ignores any password your IdP sends.
- Bulk operations, sorting, and ETags.

Airbyte returns 100 resources per SCIM response page by default. If your IdP requests a `count` above 200, Airbyte clamps it to 200. Your IdP must request additional pages to retrieve the remaining resources; this page size does not limit the total number of users or groups you can provision.

## How deactivation affects access

Deactivating or deleting a user is destructive within the organization that provisioned them. Airbyte removes:

- Their organization permissions.
- Their permissions in every workspace in the organization.
- Their membership in every group in the organization.

Airbyte keeps their user account and their access in any other organization they belong to. It also keeps the SCIM record, so your IdP can reactivate them later.

Reactivating a user only restores the baseline organization member permission. Airbyte doesn't restore the workspace roles, elevated organization roles, or group memberships they had before.

:::warning
After you reactivate someone, your IdP must re-add them to their groups, and an organization admin must re-grant any individual roles they had. Otherwise, they can sign in but only see what an organization member sees.
:::

### People in multiple organizations

SCIM doesn't control sign-in. It issues no credentials, and deactivation only affects the organization that provisioned the person, so they keep their account and their access in every other organization they belong to.

Whether someone signs in with SSO depends on [SSO](sso), not SCIM. If an organization that uses SSO has verified their email domain, they sign in through that organization's SSO, and that same account still gives them access to their other organizations, including any that don't use SSO or SCIM.

## Provision users who already have Airbyte accounts

If someone already has an Airbyte account with the email address your IdP provisions, Airbyte links the SCIM record to that existing account instead of creating a duplicate. The account keeps any elevated access it already had in your organization.

If you provision someone before they've ever signed in, Airbyte attaches their identity to the record the first time they sign in with a verified matching email address.

## Troubleshoot

Your IdP surfaces the status code Airbyte returns. Use these to narrow down the cause.

| Status | Meaning                                                                                                                                                                     |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 400    | Airbyte rejected the request body, an attribute it doesn't support, or an unsupported filter. Trim your IdP's attribute mappings to the supported attributes above.          |
| 401    | The bearer token is missing, malformed, or no longer valid. This happens after you generate a new token or disable SCIM. Paste the current token into your IdP.              |
| 403    | SCIM isn't enabled for your organization, or your plan doesn't include it. Contact Airbyte.                                                                                  |
| 404    | The user or group no longer exists in Airbyte. This is common after someone deletes a group in Airbyte while SCIM was disabled.                                              |
| 409    | Another record already uses that `userName`, email, `externalId`, or group name. Airbyte also returns this when your IdP tries to create a group that already exists in Airbyte. |
| 500    | An unexpected Airbyte error. The response includes a reference ID. Send it to [support](https://support.airbyte.com).                                                        |

Other things to check:

- **A user can't be created.** Verify that Airbyte has verified the domain of that user's email address.
- **One group never provisions.** Your IdP can't take over a group that already exists in Airbyte. Rename or delete the Airbyte group, then let your IdP create it.
- **Nobody is syncing.** Confirm SCIM is still enabled in **Organization settings** > **SSO**, and that your IdP has the current token and the base URL Airbyte shows there.

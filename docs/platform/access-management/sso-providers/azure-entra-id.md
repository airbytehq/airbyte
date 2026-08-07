---
sidebar_label: Entra ID
products: cloud
---

# Set up single sign on using Entra ID

This guide shows you how to set up Microsoft Entra ID (formerly Azure ActiveDirectory) and Airbyte so your users can log into Airbyte using your organization's identity provider (IdP) and OpenID Connect (OIDC).

## Overview

This guide is for administrators. It assumes you have:

- Basic knowledge of Entra ID, OIDC, and Airbyte
- The permissions to manage Entra ID in your organization
- Organization admin permissions for Airbyte

The steps below cover Cloud with Entra ID OIDC.

## Cloud with Entra ID OIDC

:::warning
For security purposes, Airbyte disables existing [applications](/platform/using-airbyte/configuring-api-access) used to access the Airbyte API once the user who owns the application signs in with SSO for the first time. Replace any Application secrets that were previously in use to ensure your integrations don't break.
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

# Salesforce

## Overview

:::info
Airbyte Enterprise Connectors are a selection of premium connectors available exclusively for Airbyte Self-Managed Enterprise and Airbyte Teams customers. These connectors, built and maintained by the Airbyte team, provide enhanced capabilities and support for critical enterprise systems. To learn more about enterprise connectors, please [talk to our sales team](https://airbyte.com/company/talk-to-sales).
:::

This page guides you through the process of setting up the [Salesforce](https://www.salesforce.com/) destination connector.

## Prerequisites

- [Salesforce Account](https://login.salesforce.com/) with Enterprise access or API quota purchased
- (Optional, Recommended) Dedicated Salesforce [user](https://help.salesforce.com/s/articleView?id=adding_new_users.htm&type=5&language=en_US)

:::tip

To use this connector, you'll need at least the Enterprise edition of Salesforce or the Professional Edition with API access purchased as an add-on. Reference the [Salesforce docs about API access](https://help.salesforce.com/s/articleView?id=000385436&type=1) for more information.

:::

## Setup guide

### Set up Salesforce

### Step 1: (Optional, Recommended) Create a dedicated Salesforce user

Follow the instructions below to create a profile and assign custom permission sets to grant the new user the write access needed for data you want to access with Airbyte.

[Log in to Salesforce](https://login.salesforce.com/) with an admin account.

#### 1. Create a new User:
-  On the top right of the screen, click the gear icon and then click **Setup**.
-  In the left navigation bar, under Administration, click **Users** > **Users**. Create a new User, entering details for the user's first name, last name, alias, and email. Filling in the email field will auto-populate the username field and nickname.
      - Leave `role` unspecified
      - Select `Salesforce Platform` for the User License
      - Select `Standard Platform User` for Profile.
      - Decide whether to generate a new password and notify the user.
      - Select `save`
#### 2. Create a new Permission Set:
-  Using the left navigation bar, select **Users** > **Permission Sets**
- Click `New` to create a new Permission Set.
- Give your permission set a descriptive label name (e.g., "Airbyte Data Activation"). The API name will autopopulate based on the label you give the permission set.
- For licence, leave this set to` –None—` and click `save`.
- Now that you see the permission set is created, define the permissions via Object Settings.
   - Click "Object Settings."
   - Select the `Object Name` for each object you want the user to have write access to (e.g., Accounts, Contacts, Opportunities).
   - Select “Edit” and check all the object permissions under "Object Permissions"
   - Click `Save`
   - Continue to add permissions for any objects you want Airbyte to have access to.
#### 3. Assign the Permission Set to the new User
- From the Permission Sets page, click "Manage Assignments" next to the read-only permission set you just created.
- Click "Add Assignments."
- Find and select the user you created in Step 1.
- Click `Assign`

Log into the email you used above and verify your new Salesforce account user. You'll need to set a password as part of this process. Keep this password accessible.

:::info
**Profile vs. Permission Set:** Remember that the user's profile will provide their baseline permissions. The permission set adds or restricts permissions on top of that.
**Object-Level vs. Field-Level Security:** This guide focuses on object-level read-only access. While setting up your permission set, you can stick with object-level security or define more granular controls by scrolling down within each object settings page to select read access for only needed fields.
:::

### Step 2: Set up the Salesforce connector in Airbyte

<!-- env:cloud -->

## For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Destinations and then click + New destination.
3. On the Set up the source page, select Salesforce from the Source type dropdown.
4. Enter a name for the Salesforce connector.
5. To authenticate:
   **For Airbyte Cloud**: Click **Authenticate your account** to authorize your Salesforce account. Airbyte will authenticate the Salesforce account you are already logged in to. Please make sure you are logged into the right account.
6. Toggle whether your Salesforce account is a [Sandbox account](https://help.salesforce.com/s/articleView?id=sf.deploy_sandboxes_parent.htm&type=5) or a production account.
7. Create a least one mapping that link a stream to a destination object in Salesforce.
8. Click **Set up source** and wait for the tests to complete.

<!-- /env:cloud -->


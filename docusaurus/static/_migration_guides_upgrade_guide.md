Review the following information to prepare for and execute your upgrade.

### Review the changelog

Before updating a connector, review the changelog to understand the changes and their potential impact on your existing connections. Find the changelog for any connector by navigating to the bottom of the documentation for that connector. Major version releases also include a migration guide.

### Plan for major updates

Major updates may require you to adjust connection settings or even make changes to your data pipelines. Allocate enough time and resources for this. Use the migration guide to ensure your transition process goes smoothly.

Airbyte provides tooling that guarantees safe connector version bumps and enforces automated version bumps for minor and patch updates. You always need to manually update for major version bumps.

### Self-managed plans: pin a specific version if you can't update

If you're unable to upgrade to the new version of a connector, you can pin that connector to a specific version.

1. In the navigation bar:

    - If you're on the Self-Managed Enterprise plan, click **Organization settings** > **Sources**/**Destinations**.

    - If you're on any other plan, click **Workspace settings** > **Sources**/**Destinations**.

2. Edit the entry for the connector you want to pin.

3. Set the **Default Version** to the version you want to use.

### Self-managed plans: update the local connector image

If you self-manage Airbyte, you must manually update the connector image in your local registry before proceeding with the migration. Follow the steps below.

1. In the navigation bar:

    - If you're on the Self-Managed Enterprise plan, click **Organization settings** > **Sources**/**Destinations**.

    - If you're on any other plan, click **Workspace settings** > **Sources**/**Destinations**.

2. Find the connector you want to update in the list of connectors.

    :::note
    Airbyte lists two versions, the current in-use version and the latest version available.
    :::

3. Click **Change** to update your OSS version to the latest available version.

### Update the connector version

Update each instance of the connector separately. If you have multiple instances of a connector, updating one doesn't affect the others.

1. In the navigation bar:

    - If you're on the Self-Managed Enterprise plan, click **Organization settings** > **Sources**/**Destinations**.

    - If you're on any other plan, click **Workspace settings** > **Sources**/**Destinations**.

2. Select the instance of the connector you wish to upgrade.

3. Select **Upgrade**.

4. Follow the prompt to confirm you are ready to upgrade to the new version.

### Clear data from affected streams

After upgrading a connector with a breaking change, you must refresh affected schemas and clear your data.

1. In the nav bar, click **Connections**.

2. Find the connection affected by the upgrade.

3. Click the **Schema** tab.

4. Click **Refresh source schema** (looks like <svg fill="none" data-icon="rotate" role="img" viewBox="0 0 24 24" class="inline-svg"><path fill="currentColor" d="M21 11a1 1 0 0 0-1 1 8.05 8.05 0 1 1-2.22-5.5h-2.4a1 1 0 1 0 0 2h4.53a1 1 0 0 0 1-1V3a1 1 0 0 0-2 0v1.77A10 10 0 1 0 22 12a1 1 0 0 0-1-1"></path></svg>). When Airbyte finishes, it shows you any detected schema changes.

5. Click **OK**.

6. Click **Save changes**

7. [Clear the data](/platform/operator-guides/clear) for the streams affected by this upgrade.

Once the clear is complete, you can begin syncing your data again as usual.

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

A HAR (HTTP Archive) file records the network activity between your browser and Airbyte. It's one of the most helpful things you can share with Airbyte Support, because it captures the exact requests your browser made, along with their responses and any errors.

<Tabs>
<TabItem value="chrome-edge" label="Chrome and Edge" default>

1. Open the Airbyte page where you encountered the problem.

2. Open developer tools. Press <kbd>F12</kbd>, or right-click anywhere on the page and click **Inspect**.

3. Click the **Network** tab.

4. Select **Preserve log** so requests aren't cleared when the page reloads or redirects.

5. Click **Clear** (the &#8856; icon) to remove any existing requests.

6. Reproduce the problem while developer tools stays open. Airbyte records each network request as it happens.

7. Right-click any request in the list, then click **Save all as HAR with content**.

8. Save the file to your computer.

</TabItem>
<TabItem value="firefox" label="Firefox">

1. Open the Airbyte page where you encountered the problem.

2. Open developer tools. Press <kbd>F12</kbd>, or open the application menu and click **More tools** > **Web Developer Tools**.

3. Click the **Network** tab.

4. Click the settings icon and confirm **Persist Logs** is enabled so requests aren't cleared when the page reloads or redirects.

5. Reproduce the problem while developer tools stays open. Airbyte records each network request as it happens.

6. Right-click any request in the list, then click **Save All As HAR**.

7. Save the file to your computer.

</TabItem>
<TabItem value="safari" label="Safari">

1. Enable the Develop menu if you haven't already. Click **Safari** > **Settings** > **Advanced**, then select **Show features for web developers**.

2. Open the Airbyte page where you encountered the problem.

3. Click **Develop** > **Show Web Inspector**, or press <kbd>Option</kbd>+<kbd>Cmd</kbd>+<kbd>I</kbd>.

4. Click the **Network** tab.

5. Select **Preserve Log** so requests aren't cleared when the page reloads or redirects.

6. Reproduce the problem while the Web Inspector stays open. Airbyte records each network request as it happens.

7. Click the **Export** icon and save the HAR file to your computer.

</TabItem>
</Tabs>

:::warning
HAR files can contain sensitive information, such as authentication tokens, cookies, and any data visible on the page. Only share HAR files with Airbyte Support, and let them know if there's anything you want to review or redact first.
:::

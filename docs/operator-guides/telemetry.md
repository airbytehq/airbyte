---
products: all
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Telemetry

Airbyte collects telemetry data in the UI and the servers to help us understand users and their use-cases better to improve the product.

Also check our [privacy policy](https://airbyte.com/privacy-policy) for more details.

<Tabs groupId="cloud-hosted">
  <TabItem value="self-managed" label="Self Managed">
      To disable telemetry for your instance, modify the `.env` file and define the following environment variable:

      ```
      TRACKING_STRATEGY=logging
      ```
  </TabItem>
  <TabItem value="cloud" label="Cloud">
    When visiting the webapp or our homepage the first time, you'll be asked for your consent to
    telemetry collection depending on the legal requirements of your location.

    To change this later go to **Settings** > **User Settings** > **Cookie Preferences** or **Cookie Preferences** in the footer of our [homepage](https://airbyte.com).

    Server side telemetry collection can't be changed using Airbyte Cloud.
  </TabItem>
</Tabs>
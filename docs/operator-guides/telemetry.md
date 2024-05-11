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
  <TabItem value="pyairbyte" label="PyAirbyte">
    When running [PyAirbyte](https://docs.airbyte.com/pyairbyte) for the first time on a new machine, you'll be informed that anonymous
    usage data is collected, along with a link to this page for more information.

    Anonymous usage tracking ("telemetry") helps us understand how PyAirbyte is being used,
    including which connectors are working well and which connectors are frequently failing. This helps
    us to prioritize product improvements which benefit users of PyAirbyte as well as Airbyte Cloud,
    OSS, and Enterprise.

    We will _never_ collect any information which could be considered PII (personally identifiable
    information) or sensitive data. We _do not_ collect IP addresses, hostnames, or any other
    information that could be used to identify you or your organization.

    You can opt-out of anonymous usage reporting by setting the environment variable `DO_NOT_TRACK`
    to any value.

  </TabItem>
</Tabs>

---
products: all
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Telemetry

Airbyte collects telemetry data from the UI and the servers to help improve the product. See Airbyte's [privacy policy](https://airbyte.com/privacy-policy) for more details.

If you'd like to turn off telemetry data collection, follow the directions below.

<Tabs groupId="cloud-hosted">
  <TabItem value="self-managed-v1" label="Self-Managed (Helm Chart V1)">
      To disable telemetry for your instance, modify the `values.yaml` file and override the hardcoded telemetry setting using component-specific `env_vars` sections:

      ```yaml
      # Override telemetry for server component
      server:
        env_vars:
          TRACKING_STRATEGY: logging

      # Override telemetry for worker component  
      worker:
        env_vars:
          TRACKING_STRATEGY: logging
      ```

  </TabItem>
  <TabItem value="self-managed-v2" label="Self-Managed (Helm Chart V2)">

  To turn off telemetry for your instance, modify your `values.yaml` file and define the following environment variable:

  ```yaml title="values.yaml"
  global:
    tracking:
      strategy: logging
  ```
  </TabItem>

  <TabItem value="cloud" label="Cloud">

  When opening Airbyte or Airbyte's homepage the first time, you're asked for your consent to telemetry collection depending on the legal requirements of your location.

  To change this later, do one of the following.
  
  - In Airbyte, go to **Settings** > **User Settings** > **Cookie Preferences**.
  - On Airbyte's website, click **Cookie Preferences** in the footer of our [homepage](https://airbyte.com).

  You can't change server-side telemetry collection in Airbyte Cloud.

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

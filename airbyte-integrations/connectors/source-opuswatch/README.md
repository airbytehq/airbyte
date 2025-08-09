# OPUSWatch
This directory contains the manifest-only connector for `source-opuswatch`.

## Unlock Horticultural Insights with Airbyte and OPUSWatch

**What is OPUSWatch?**
OPUSWatch is a smart wearable solution developed by OPUS Solutions B.V., based in the Netherlands. This innovative smartwatch is specifically designed for the horticulture industry to digitize and streamline various operational processes within greenhouses and nurseries. It empowers growers to gain real-time insights into their labor, productivity, and overall operations. Employees use the OPUSWatch to easily record their tasks, track their work on specific crops, and even manage orders directly from their wrist. This data is then fed into a central system for analysis and decision-making.

Website: opuswatch.nl

**What does the OPUSWatch Airbyte Connector do?**
The Airbyte connector for OPUSWatch allows you to seamlessly extract valuable data from the OPUSWatch platform and load it into your data warehouse or lake. By connecting OPUSWatch to Airbyte, you can centralize your horticultural operational data with other business-critical information, enabling comprehensive analysis and reporting.

**With the OPUSWatch Airbyte connector, you can retrieve the following streams of data:**
* **Clients:** Information about your clients or customers.
* **Locations:** Details about the different locations or areas within your greenhouse or nursery.
* **Rows:** Data pertaining to the specific rows or sections where plants are cultivated.
* **Users:** Information about the individuals who have access to the OPUSWatch system.
* **Workers:** Details about your workforce, including their identification and potentially other relevant attributes.
* **Worker Groups:** Information about how your workers are organized into teams or groups.
* **Tasks:** Data on the various activities or jobs that are performed by workers.
* **Task Groups:** Information about how tasks are categorized or grouped together.
* **Labels:** Details about the different labels used for plants, products, or processes.
* **Varieties:** Information on the different plant varieties being cultivated.
* **Registrations Initial:** A snapshot of initial work registrations recorded by the OPUSWatch devices.
* **Registrations Incremental:** Updates and new work registrations recorded by the OPUSWatch devices since the last synchronization.
* **Sessions Initial:** A snapshot of initial work sessions or periods tracked by the OPUSWatch devices.
* **Sessions Incremental:** Updates and new work sessions or periods tracked by the OPUSWatch devices since the last synchronization.

By leveraging the OPUSWatch Airbyte connector, horticultural businesses can break down data silos and gain a holistic view of their operations. This enables data-driven decision-making for optimizing labor allocation, improving productivity, and ultimately enhancing the efficiency of their greenhouse or nursery operations.

## Usage
There are multiple ways to use this connector:
- You can use this connector as any other connector in Airbyte Marketplace.
- You can load this connector in `pyairbyte` using `get_source`!
- You can open this connector in Connector Builder, edit it, and publish to your workspaces.

Please refer to the manifest-only connector documentation for more details.

## Local Development
We recommend you use the Connector Builder to edit this connector.

But, if you want to develop this connector locally, you can use the following steps.

### Environment Setup
You will need `airbyte-ci` installed. You can find the documentation [here](airbyte-ci).

### Build
This will create a dev image (`source-opuswatch:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-opuswatch build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-opuswatch test
```


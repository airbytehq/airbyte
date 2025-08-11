---
products: all
---

# Data activation (reverse ETL)

:::info
Data activation is in early access. If you'd like to be an early adopter, [fill out this form](https://form.typeform.com/to/STc7a0jx).
:::

Data activation enables you to move data out of your data warehouse and into the operational tools where work happens, like CRMs, marketing platforms, and support systems. With this capability, you can deliver modeled data directly to points of action and systems people already use, helping your organization respond faster and more effectively.

This page introduces the concept of data activation, outlines how it works within the Airbyte platform, and describes common use cases.

![Conceptual diagram showing data moving from a source, fields being mapped, and then moving to a destination](assets/data-activation-concept.png)

## What's data activation?

Data Activation operationalizes data by syncing it from storage systems&mdash;typically data warehouses&mdash;into the tools that business teams use daily. These tools include platforms like Salesforce, HubSpot, Marketo, Zendesk, and others.

Instead of limiting insights to dashboards and reports, data activation enables data to directly power workflows and decisions in real time in the places people need it.

The terms "data activation" and "reverse ETL" are sometimes used interchangeably, even if there is nuance in their meaning. Airbyte prefers the term data activation as a blanket term. It reflects the goal of any reverse ETL pipeline: to _activate your data_ by giving it to the people who need it in the places where it has the greatest impact on their work.

### Key characteristics

- **Warehouse-to-app sync**: transfer data from warehouses (e.g., Snowflake, BigQuery, Redshift) to operational destinations like Salesforce or Customer.io.

- **Reverse ETL**: a method used in data activation to extract, transform, and load data from warehouses into SaaS tools.

- **Declarative mapping**: You define how data fields map and transform between the warehouse and the destination.

- **Broad application**: data activation supports a range of business functions, including go-to-market operations, customer success, finance, and support.

## Why data activation is useful in Airbyte

Data Activation complements Airbyte’s existing data movement capabilities by enabling outbound syncs from your warehouse into operational tools. It expands the value of centralized data by delivering insights to where the action is.

### Benefits

- **Improved decision-making**: Sales teams can access lead scores directly within CRM platforms.

- **Personalized marketing**: Marketing teams can target users based on product usage and engagement.

- **Context-aware support**: Support teams can prioritize tickets using customer health metrics synced into their service tools.

This process turns your data warehouse into a central intelligence hub and ensures insights reach the systems—and people—who need them.

## How data activation works in Airbyte

Data activation works like any other sync, by moving data from a source to a destination. The process typically involves three stages:

1. **Ingestion**: Sync data from your sources to your data warehouse destination using Airbyte's connectors.

2. **Transformation**: Model and prepare your data using tools like dbt or SQL.

3. **Activation**: Sync that modeled data to operational tools using Airbyte's connectors and declarative mappings.

## Use Cases

Data Activation aligns with the shift toward operational analytics in modern data architectures. As organizations consolidate their data into warehouses, there is increasing demand for that data to inform business decisions beyond dashboards and reports.

Teams in sales, marketing, support, and finance often rely on operational systems that are disconnected from your data warehouse. Data activation bridges this gap, replacing manual exports, ad hoc pipelines, or no data at all with automated, governed workflows.

### Example: Revenue operations

- **User**: Revenue Operations Manager.

- **Objective**: Help sales reps prioritize high-intent accounts.

- **Challenge**: Usage metrics exist in Snowflake, but sales reps work in Salesforce.

- **Solution**: Use Airbyte to sync product usage scores from your data warehouse to custom fields in Salesforce.

- **Result**: Reps can view up-to-date engagement scores directly in their CRM and prioritize outreach accordingly.

### Additional use cases

| Use Case               | Description                                                       |
| ---------------------- | ----------------------------------------------------------------- |
| Marketing Automation   | Sync audience segments to HubSpot or Braze for targeted campaigns |
| Customer 360           | Push enriched customer profiles into CRMs for better visibility    |
| Support Triage         | Deliver customer health scores to Zendesk for prioritization      |
| Finance Reconciliation | Notify finance teams via Slack when you detect billing anomalies   |

## Get started

To start activating your data with Airbyte, see the following topics.

- [Set up a source](../using-airbyte/getting-started/add-a-source)
- [Set up a destination](../using-airbyte/getting-started/add-a-destination)
- [Set up a connection](add-connection)

More resources:

- [All Airbyte connectors](/integrations)
- [dbt Core](https://www.getdbt.com/)

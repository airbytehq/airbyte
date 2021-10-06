---
description: 'Here''s what''s coming in the next few days, weeks, months, and years!'
---

# Roadmap

## Coming within a few days

Check out our [Roadmap for Core](https://github.com/airbytehq/airbyte/milestones) and our [Roadmap for Connectors](https://github.com/airbytehq/airbyte/projects/3) on GitHub. You'll see the features we're currently working on or about to. You may also give us insights, by adding your own issues and voting for specific features / integrations.

## Coming within a few weeks / months

We understand that we're not "production-ready" for a lot of companies yet. In the end, we just got started in July 2020, so we're at the beginning of the journey. Here is a highlight of the main features we are planning on releasing in the next few months:

**Landing in August or so:**

* Release of Airbyte Cloud's private beta. 
* Support of most popular databases as both sources and destinations.
* Support of data lakes, including Delta Lake soon.
* Adapt automatically to sources' schema changes.
* OAuth support for connector configuration \([\#768](https://github.com/airbytehq/airbyte/issues/768)\).

**Coming a bit later:**

* Airbyte Cloud release. 
* Support for creating destination connectors with the CDK.
* Our declarative interface \(CLI\).
* Credential and secrets vaulting \([\#837](https://github.com/airbytehq/airbyte/issues/837)\).
* Webhook connector.

Our goal is to become "production-ready" for any company whatever their data stack, infrastructure, architecture, data volume, and connector needs. **If you see anything missing in this list that you would need before deploying us in prod, please talk to us via** [**Slack**](https://slack.airbyte.io) **or** [**email**](mailto:contact@airbyte.io)**!**

## Coming within a few quarters / years

We also wanted to share with you how we think about the high-level roadmap over the next few months and years. We foresee several high-level phases that we will try to share here.

### **1. Parity on data consolidation (ELT) in warehouses / databases**

Our first focus is to support batch-type ELT integrations. We feel that we can provide value right away as soon as we support one of the integrations you need. Batch integrations are also easier to build and sustain. So we would rather start with that.

Before we move on to the next phase, we want to make sure we are supporting all the major integrations and that we are in a state where we can address the long tail, with the help of the community.

We also want to fully integrate with the open-source ecosystem, including Airflow, dbt, Kubernetes, GreatExpectations, etc., so teams have the ability to fully build the data infrastructure they need.

### **2. Reverse-ETL from warehouses / databases**

Some integrations we have in mind are batch distribution integrations, from warehouses to third-party tools. For instance, a use case could be if your marketing team wants to send back the data to your ad platforms, so it can better optimize the campaigns. Another use case could be syncing the consolidated data back to your CRM.

It’s not yet clear in our minds when to prioritize those additional integrations. We will have a better idea once we see the feedback we get from the community we build with data consolidation.

### **3. Parity with enterprise features: data quality, privacy compliance, customer data consolidation features, etc.**

Hopefully, we will have raised a Series-A by then, so we can start focusing on the enterprise edition’s features, in addition to pursuing efforts on addressing the long tail of integrations.

Those enterprise features comprise:

* Hosting and management
* User and role access management
* SSO
* Privacy compliance \(GDPR, CCPA, etc\)
* Customer data consolidation with identity resolution

### **4. Expand on all data engineering features**

This is when we will start differentiating ourselves in terms of feature coverage with current cloud-based incumbents. Being open-sourced enables us to go faster, but also deeper.

We are also thinking about supporting streaming-type integrations, a la Segment.


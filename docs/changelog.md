---
description: Be sure to not miss out on new features and improvements!
---

# Changelog

Airbyte is not built on top of Singer, but is compatible with Singer's protocol. Airbyte's ambitions go beyond what Singer enables to do, so we are building our own protocol that will keep its compatibility with Singer's one.

## 0.4.0 - expected around 10/30/2020

Here is what we have in mind:

* our own **Snowflake** warehouse integration
* **10 additional Singer taps** 

## 0.3.0 - expected around 10/23/2020

Here is what we have in mind:

* new guides \(how to build scratch/singer\) 
* our own **BigQuery** warehouse integration 
* our own **PostGres** warehouse integration 
* **5 additional Singer taps**

## 0.2.0 - expected around 10/16/2020

Here is what we are working on right now:

* **a new Admin section** to enable users to add their own connectors, in addition to upgrading the ones they currently use 
* improve the developer experience \(DX\) for **contributing new connectors** with additional documentation and a connector protocol 
* as a bonus if we can, update the onboarding experience with pre-filled demo data for the users who just want to see how Airbyte works with the least effort.
* simplify the process of supporting new Singer taps, ideally make it a 1-day process

Here is the [UI we're building](https://www.figma.com/file/pO3Ob5W0yKUFOQzvg8TR3z/Airbyte?node-id=0%3A1) for that release, if you're curious :\)

## 0.1.0 - delivered on 09/23/2020

This is our very first release after 2 months of work.

* **New sources:** Stripe, Postgres
* **New destinations:** BigQuery, Postgres
* **Only one destination**: we only support one destination in that 1st release, but you will soon be able to add as many as you need. 
* **Logs & monitoring**: you can now see your detailed logs
* **Scheduler:** you now have 10 different frequency options for your recurring syncs
* **Deployment:** you can now deploy Airbyte via a simple Docker image, or directly on AWS and GCP
* **New website**: this is the day we launch our website - airbyte.io. Let us know what you think
* **New documentation:** this is the 1st day for our documentation too
* **New blog:** we published a few articles on our startup journey, but also about our vision to making data integrations a commodity. 

Stay tuned, we will have new sources and destinations very soon! Don't hesitate to subscribe to our [newsletter](https://airbyte.io/#subscribe-newsletter) to receive our product updates and community news.


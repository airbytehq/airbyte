# Business Model

We will have several business models, between our self-hosted solution and our hosted one. 

Let's start with self-hosted solution. 

## **1. Self-hosted solution**
We will have a community edition that will stay in MIT license, and a source-available enterprise edition.

Note that **the open-source codebase will never contain arbitrary limits** \(e.g., event volumes, user numbers\).

### **Community edition**

Our philosophy is that every feature that serves the individual contributor should be in the community edition. Our goal is to make all the integration pipelines open-sourced with the MIT license. These pipelines should become a commodity for any engineering team, and we want to accelerate this trend.

In addition to the integration pipelines, the community edition will include orchestrating and scheduling data pipelines, but also all the integrations with the data stack (Airflow, Dagster, DBT, etc).  

To achieve our vision that data integration pipelines should be a commodity, we want to create the open-source standard for our industry to leverage. An enterprise edition of our product cannot succeed without the success of the community edition. So, for now, we’re focusing 100% of our time on the community edition, and will continue to do so for quite a while.

### **Enterprise edition**

At some point, when we feel that Airbyte has become the open-source standard to move data, we will start focusing on features that will make more sense to enterprises. These features will stay **source-available** but will be sold and not open-sourced.

The enterprise edition is essential for us, as we will need the revenues to grow our team. A larger team will help us build more features and, eventually, a better product.

Some features that we’re considering for the enterprise edition:

* Hosting management
* Data quality protocols
* Privacy compliance with GDPR, CCPA, etc.
* Role and access management
* Single-Sign On

This is just a snapshot about our current state of mind. We will learn a lot along the way and our vision of the enterprise edition will surely evolve. And please don’t hesitate to share about your companies’ pain points that we can help solve.

## **2. Hosted solution**

In the future, we will also offer a hosted solution for the teams that don't want to manage the connectors in their infrastructure. That offer will be closer to what Fivetran and StitchData offers, but the difference will be with the flexibility and control that you would get with Airbyte, given it's open-source.

## **3. Powered by Airbyte**

One last business model, which was brought to us by the community, is what we call "Powered by Airbyte". We’d empower you to offer integrations to your own clients on your platform, using our white-labeled connectors through our API. So, instead of building N connectors on your platform with your engineering team and investing a lot of time on that, you would just leverage Airbyte's connectors for that. 



# Fivetran vs Airbyte

We wrote an article, “[Open-source vs. Commercial Software: How to Solve the Data Integration Problem](https://airbyte.io/articles/data-engineering-thoughts/open-source-vs-commercial-software-how-to-better-solve-data-integration/),” in which we describe the pros and cons of Fivetran’s commercial approach and Airbyte’s open-source approach. Don’t hesitate to check it out for more detailed arguments. As a summary, here are the differences:

![](https://airbyte.io/wp-content/uploads/2021/01/Airbyte-vs-Fivetran.png)

## **Fivetran:**

* **Limited high-quality connectors:** after 8 years in business, Fivetran supports 150 connectors. The more connectors, the more difficult it is for Fivetran to keep the same level of maintenance across all connectors. They will always have a ROI consideration to maintaining long-tailed connectors. 
* **Pricing indexed on usage:** Fivetran’s pricing is indexed on the number of active rows \(rows added or edited\) per month. Teams always need to keep that in mind and are not free to move data without thinking about cost, as the costs can grow fast. 
* **Security and privacy compliance:** all companies are subject to privacy compliance laws, such as GDPR, CCPA, HIPAA, etc. As a matter of fact, above a certain stage \(about 100 employees\) in a company, all external products need to go through a security compliance process that can take several months. 
* **No moving data between internal databases:** Fivetran sits in the cloud, so if you have to replicate data from an internal database to another, it makes no sense to have the data move through them \(Fivetran\) for privacy and cost reasons. 

## **Airbyte:**

* **Free, as open source, so no more pricing based on usage**: learn more about our [future business model](https://handbook.airbyte.io/strategy/business-model) \(connectors will always remain open source\). 
* **Supporting 60 connectors within 8 months from inception**.  Our goal is to reach 200+ connectors by the end of 2021. 
* **Building new connectors made trivial, in the language of your choice:** Airbyte makes it a lot easier to create your own connector, vs. building them yourself in-house \(with Airflow or other tools\). Scheduling, orchestration, and monitoring comes out of the box with Airbyte.
* **Addressing the long tail of connectors:** with the help of the community, Airbyte ambitions to support thousands of connectors. 
* **Adapt existing connectors to your needs:** you can adapt any existing connector to address your own unique edge case.
* **Using data integration in a workflow:** Airbyte’s API lets engineering teams add data integration jobs into their workflow seamlessly. 
* **Integrates with your data stack and your needs:** Airflow, Kubernetes, dbt, etc. Its normalization is optional, it gives you a basic version that works out of the box, but also allows you to use dbt to do more complicated things.
* **Debugging autonomy:** if you experience any connector issue, you won’t need to wait for Fivetran’s customer support team to get back to you, if you can fix the issue fast yourself. 
* **No more security and privacy compliance, as self-hosted, source-available and open-sourced \(MIT\)**. Any team can directly address their integration needs.

Your data stays in your cloud. Have full control over your data, and the costs of your data transfers.


# Meltano vs Airbyte

We wrote an article, “[The State of Open-Source Data Integration and ETL](https://airbyte.io/articles/data-engineering-thoughts/the-state-of-open-source-data-integration-and-etl/),” in which we list and compare all ETL-related open-source projects, including Meltano and Airbyte. Don’t hesitate to check it out for more detailed arguments. As a summary, here are the differences:

## **Meltano:**

* **Meltano is built on top of the Singer protocol, whereas Airbyte is built on top of the Airbyte protocol**. Having initially created Airbyte on top of Singer, we wrote about why we didn't move forward with it [here](https://airbyte.io/blog/why-you-should-not-build-your-data-pipeline-on-top-of-singer) and [here](https://airbyte.io/blog/airbyte-vs-singer-why-airbyte-is-not-built-on-top-of-singer). Summarized, the reasons were: Singer connectors didn't always adhere to the Singer protocol, had poor standardization and visibility in terms of quality, and community governance and support was abandoned by Stitch. By contrast, we aim to make Airbyte a product that ["just works"](https://airbyte.io/blog/our-truth-for-2021-airbyte-just-works) and always plan to maximize engagement within the Airbyte community. 
* **CLI-first approach:** Meltano was primarily built with a command line interface in mind. In that sense, they seem to target engineers with a preference for that interface.
* **Integration with Airflow for orchestration:** You can either use Meltano alone for orchestration or with Airflow; Meltano works both ways.  
* All connectors must use Python.  
* Meltano works with any of Singer's 200+ available connectors. However, in our experience, quality has been hit or miss. 

## **Airbyte:**

In contrast, Airbyte is a company fully committed to the open-source project and has a [business model](https://handbook.airbyte.io/strategy/business-model) in mind around this project. Our [team](https://airbyte.io/about-us) are data integration experts that have built more than 1,000 integrations collectively at large scale. The team now counts 20 engineers working full-time on Airbyte.

* **Airbyte supports more than 100 connectors after only 1 year since its inception**, 20% of which were built by the community. Our ambition is to support **200+ connectors by the end of 2021.** 
* Airbyte’s connectors are **usable out of the box through a UI and API,** with monitoring, scheduling and orchestration. Airbyte was built on the premise that a user, whatever their background, should be able to move data in 2 minutes. Data engineers might want to use raw data and their own transformation processes, or to use Airbyte’s API to include data integration in their workflows. On the other hand, analysts and data scientists might want to use normalized consolidated data in their database or data warehouses. Airbyte supports all these use cases.  
* **One platform, one project with standards:** This will help consolidate the developments behind one single project, some standardization and specific data protocol that can benefit all teams and specific cases. 
* **Not limited by Singer’s data protocol:** In contrast to Meltano, Airbyte was not built on top of Singer, but its data protocol is compatible with Singer’s. This means Airbyte can go beyond Singer, but Meltano will remain limited. 
* **Connectors can be built in the language of your choice,** as Airbyte runs them as Docker containers.
* **Airbyte integrates with your data stack and your needs:** Airflow, Kubernetes, dbt, etc. Its normalization is optional, it gives you a basic version that works out of the box, but also allows you to use dbt to do more complicated things.

## **Other noteworthy differences:**

* In terms of community, Meltano's Slack community got 430 new members in the last 6 months, while Airbyte got 800. 
* The difference in velocity in terms of feature progress is easily measurable as both are open-source projects. Meltano closes about 30 issues per month, while Airbyte closes about 120. 


# Meltano vs Airbyte

We wrote an article, “[The State of Open-Source Data Integration and ETL](https://airbyte.io/articles/data-engineering-thoughts/the-state-of-open-source-data-integration-and-etl/),” in which we list and compare all ETL-related open-source projects, including Meltano and Airbyte. Don’t hesitate to check it out for more detailed arguments. As a summary, here are the differences:
![](https://airbyte.io/wp-content/uploads/2020/10/Landscape-of-open-source-data-integration-platforms-4.png)

## **Meltano:**

Meltano is a Gitlab side project. Since 2019, they have been iterating on several approaches. The latest positioning is an orchestrator dedicated to data integration that was built by Gitlab on top of Singer’s taps and targets. They now have only three maintainers for this project.

* **Only 28 connectors built on top of Singer, after 2 years**. This means that Meltano has the same limitations as Singer in regards to its data protocol, and quality of connectors. 
* **CLI-first approach:** Meltano was primarily built with a command line interface in mind. In that sense, they seem to target engineers with a preference for that interface. Unfortunately, it’s not thought to be part of some workflows. 
* **A new UI**: Meltano has recently built a new UI to try to appeal to a larger audience. 
* **Integration with DBT for transformation:** Meltano offers some deep integration with [DBT](http://getdbt.com), and therefore lets data engineering teams handle transformation any way they want. 
* **Integration with Airflow for orchestration:** You can either use Meltano alone for orchestration or with Airflow; Meltano works both ways.  

## **Airbyte:**

In contrast, Airbyte is a company fully committed to the open-source MIT project and has a [business model](../../company-handbook/business-model.md)in mind around this project. Our [team](../../company-handbook/team.md) are data integration experts that have built more than 1,000 integrations collectively at large scale. The team now counts 20 engineers working full-time on Airbyte.

* **Airbyte supports 60 connectors after only 8 months since its inception**, 20% of which were built by the community. Our ambition is to support **200+ connectors by the end of 2021.** 
* Airbyte’s connectors are **usable out of the box through a UI and API,** with monitoring, scheduling and orchestration. Airbyte was built on the premise that a user, whatever their background, should be able to move data in 2 minutes. Data engineers might want to use raw data and their own transformation processes, or to use Airbyte’s API to include data integration in their workflows. On the other hand, analysts and data scientists might want to use normalized consolidated data in their database or data warehouses. Airbyte supports all these use cases.  
* **One platform, one project with standards:** This will help consolidate the developments behind one single project, some standardization and specific data protocol that can benefit all teams and specific cases. 
* **Not limited by Singer’s data protocol:** In contrast to Meltano, Airbyte was not built on top of Singer, but its data protocol is compatible with Singer’s. This means Airbyte can go beyond Singer, but Meltano will remain limited. 
* **Connectors can be built in the language of your choice,** as Airbyte runs them as Docker containers.
* **Airbyte integrates with your data stack and your needs:** Airflow, Kubernetes, DBT, etc. Its normalization is optional, it gives you a basic version that works out of the box, but also allows you to use DBT to do more complicated things.

## **Other noteworthy differences:**
* In terms of community, Meltano's Slack community got 430 new members in the last 6 months, while Airbyte got 800. 
* The difference in velocity in terms of feature progress is easily measurable as both are open-source projects. Meltano closes about 30 issues per month, while Airbyte closes about 120. 


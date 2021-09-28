# Pipelinewise vs Airbyte

## **PipelineWise:**

PipelineWise is an open-source project by Transferwise that was built with the primary goal of serving their own needs. There is no business model attached to the project, and no apparent interest in growing the community.

* **Supports 21 connectors,** and only adds new ones based on the needs of the mother company, Transferwise. 
* **No business model attached to the project,** and no apparent interest from the company in growing the community. 
* **As close to the original format as possible:** PipelineWise aims to reproduce the data from the source to an Analytics-Data-Store in as close to the original format as possible. Some minor load time transformations are supported, but complex mapping and joins have to be done in the Analytics-Data-Store to extract meaning.
* **Managed Schema Changes:** When source data changes, PipelineWise detects the change and alters the schema in your Analytics-Data-Store automatically.
* **YAML based configuration:** Data pipelines are defined as YAML files, ensuring that the entire configuration is kept under version control.
* **Lightweight:** No daemons or database setup are required.

## **Airbyte:**

In contrast, Airbyte is a company fully committed to the open-source project and has a [business model in mind](https://handbook.airbyte.io/) around this project.

* Our ambition is to support **300+ connectors by the end of 2021.** We already supported about 50 connectors at the end of 2020, just 5 months after its inception.
* Airbyte’s connectors are **usable out of the box through a UI and API,** with monitoring, scheduling and orchestration. Airbyte was built on the premise that a user, whatever their background, should be able to move data in 2 minutes. Data engineers might want to use raw data and their own transformation processes, or to use Airbyte’s API to include data integration in their workflows. On the other hand, analysts and data scientists might want to use normalized consolidated data in their database or data warehouses. Airbyte supports all these use cases.  
* **One platform, one project with standards:** This will help consolidate the developments behind one single project, some standardization and specific data protocol that can benefit all teams and specific cases. 
* **Connectors can be built in the language of your choice,** as Airbyte runs them as Docker containers.
* **Airbyte integrates with your data stack and your needs:** Airflow, Kubernetes, dbt, etc. Its normalization is optional, it gives you a basic version that works out of the box, but also allows you to use dbt to do more complicated things.

The data protocols for both projects are compatible with Singer’s. So it is easy to migrate a Singer tap or target onto Airbyte or PipelineWise.


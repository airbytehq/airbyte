# Singer vs Airbyte

If you want to understand the difference between Airbyte and Singer, you might be interested in 2 articles we wrote:

* “[Airbyte vs. Singer: Why Airbyte is not built on top of Singer](https://airbyte.io/articles/data-engineering-thoughts/airbyte-vs-singer-why-airbyte-is-not-built-on-top-of-singer/).”
* “[The State of Open-Source Data Integration and ETL](https://airbyte.io/articles/data-engineering-thoughts/the-state-of-open-source-data-integration-and-etl/),” in which we list and compare all ETL-related open-source projects, including Singer and Airbyte. As a summary, here are the differences:

![](https://airbyte.io/wp-content/uploads/2020/10/Landscape-of-open-source-data-integration-platforms-4.png)

## **Singer:**

* **Supports 96 connectors after 4 years.**
* **Increasingly outdated connectors:** Talend \(acquirer of StitchData\) seems to have stopped investing in maintaining Singer’s community and connectors. As most connectors see schema changes several times a year, more and more Singer’s taps and targets are not actively maintained and are becoming outdated. 
* **Absence of standardization:** each connector is its own open-source project. So you never know the quality of a tap or target until you have actually used it. There is no guarantee whatsoever about what you’ll get.
* **Singer’s connectors are standalone binaries:** you still need to build everything around to make them work \(e.g. UI, configuration validation, state management, normalization, schema migration, monitoring, etc\). 
* **No full commitment to open sourcing all connectors,** as some connectors are only offered by StitchData under a paid plan.  _\*\*_

## **Airbyte:**

* Our ambition is to support **300+ connectors by the end of 2021.** We already supported about 50 connectors at the end of 2020, just 5 months after its inception. 
* Airbyte’s connectors are **usable out of the box through a UI and API**, with monitoring, scheduling and orchestration. Airbyte was built on the premise that a user, whatever their background, should be able to move data in 2 minutes. Data engineers might want to use raw data and their own transformation processes, or to use Airbyte’s API to include data integration in their workflows. On the other hand, analysts and data scientists might want to use normalized consolidated data in their database or data warehouses. Airbyte supports all these use cases.  
* **One platform, one project with standards:** This will help consolidate the developments behind one single project, some standardization and specific data protocol that can benefit all teams and specific cases. 
* **Connectors can be built in the language of your choice,** as Airbyte runs them as Docker containers.
* **Airbyte integrates with your data stack and your needs:** Airflow, Kubernetes, dbt, etc. Its normalization is optional, it gives you a basic version that works out of the box, but also allows you to use dbt to do more complicated things.
* **A full commitment to the open-source MIT project** with the promise not to hide some connectors behind paid walls.

Note that Airbyte’s data protocol is compatible with Singer’s. So it is easy to migrate a Singer tap onto Airbyte.


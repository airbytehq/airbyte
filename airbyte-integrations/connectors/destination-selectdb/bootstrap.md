# SelectDB destination


SelectDB destination adopts MySQL protocol(JDBC) and copy into to exchange data. 

1. JDBC is used to manipulate the data table structure and execute the create table statement before data import
2. Copy Into is an import method based on Object storage, For SelectDB destination, first upload csv file into selectdb internal stage, and then copy into SelectDB with transaction operation.

## Introduction to SelectDB

SelectDB is a cloud-native realtime data warehouse built by the core developers of Apache Doris based on the Apache Doris open source project.
[SelectDB](https://en.selectdb.com/docs/selectdb)

### Core Features

- **Extremely fast** : In terms of storage, it adopts efficient columnar storage and data indexing; in terms of computing, it relies on the MPP distributed computing architecture and the vectorized execution engine optimized for X64 and ARM64; in the ClickBench public performance evaluation, it is at the world's leading level.
- **Single unified** : It can run multiple analytical workloads on a single system. It supports real-time/interactive/batch computing types, structured/semi-structured data types, and federated querying with external data lakes and databases.
- **Easy to use** : Compatible with MySQL network protocols; powerful and easy-to-use WebUI-based database management tools, and rich connectors for integration with Spark/Flink/dbt/Kafka.
- **Cost-effective** : Deeply adapted to the cloud platforms, and adopts an implementation architecture that separates storage and computing. In terms of computing, it provides on-demand automatic expansion and contraction, and the storage adopts tiered storage of hot and cold data.
- **Open** : It is developed based on the open source Apache Doris, and data can be freely migrated with Doris. Runs on multiple clouds and provides a consistent user experience.
- **Enterprise-grade features** : provides user authentication and access control, data protection and backup. In the future, it will also provide data masking, finer-grained authority control, and data lineage to meet the needs of data governance.


### Difference with Apache Doris

SelectDB is developed based on the Apache Doris. SelectDB will continue to work with the Doris community to strengthen the open source kernel. At the same time, SelectDB also provides the following enhanced features and services for enterprise customers.
- **Apache Doris LTS version** : Provides up to 18 months of Apache Doris LTS version to meet the needs of enterprises for stronger stability of Doris. This version is free and the code is open source.
- **Cloud-native kernel** : In addition to the enhancement of the open source Doris kernel, it also provides a deeply adapted cloud-native kernel for public cloud platforms, so as to provide enterprises with best price / performance and enterprise-grade features.
- **Native management tools** : provides powerful and easy-to-use web-based database management and development tools. It can be used to replace tools like Navicat.
- **Professional technical support** : Professional technical support services are provided for open source Apache Doris and SelectDB products.

### Two Product Editions

According to the needs of different enterprises, there are currently two editions for SelectDB:

- **SelectDB Cloud：** A fully managed data warehouse as a service on public clouds.
- **SelectDB Enterprise：** Delivered as on-premises software, deployed in your IDC or VPC of public cloud.

SelectDB 1.0 was opened for trial application in July 2022, and dozens of companies have already tried it.

The SelectDB 2.0 preview is now open for trial application. Starting from SelectDB 2.0, SelectDB has also officially launched the international site. If customers want to use AWS, Azure and GCP, please visit SelectDB International Station; if customers want to use Alibaba Cloud, Tencent Cloud and Huawei Cloud, please visit SelectDB China Station.
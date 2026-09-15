# Doris destination


Doris destination adopts MySQL protocol(JDBC) and Doris Stream Load to exchange data. 

1. JDBC is used to manipulate the data table structure and execute the create table statement before data import
2. Stream Load is a synchronous import method based on HTTP/HTTPS, For Doris destination, first pre-write csv file, and then write to doris with Stream Load transaction operation.

## Introduction to Apache Doris

Apache Doris is a high-performance, real-time analytical database based on MPP architecture, known for its extreme speed and ease of use. It only requires a sub-second response time to return query results under massive data and can support not only high-concurrent point query scenarios but also high-throughput complex analysis scenarios. Based on this, Apache Doris can better meet the scenarios of report analysis, ad-hoc query, unified data warehouse, Data Lake Query Acceleration, etc. Users can build user behavior analysis, AB test platform, log retrieval analysis, user portrait analysis, order analysis, and other applications on top of this.
[https://doris.apache.org/docs/summary/basic-summary](https://doris.apache.org/docs/summary/basic-summary)


## Technical Overview
The overall architecture of Apache Doris is shown in the following figure. The Doris architecture is very simple, with only two types of processes.

#### Frontend（FE）: 
##### It is mainly responsible for user request access, query parsing and planning, management of metadata, and node management-related work.
#### Backend（BE）: 
##### It is mainly responsible for data storage and query plan execution.

Both types of processes are horizontally scalable, and a single cluster can support up to hundreds of machines and tens of petabytes of storage capacity. And these two types of processes guarantee high availability of services and high reliability of data through consistency protocols. This highly integrated architecture design greatly reduces the operation and maintenance cost of a distributed system.

Apache Doris adopts MySQL protocol, highly compatible with MySQL dialect, and supports standard SQL. Users can access Doris through various client tools and support seamless connection with BI tools.

[Stream load](https://doris.apache.org/docs/data-operate/import/import-way/stream-load-manual/) is a synchronous way of importing. Users import local files or data streams into Doris by sending HTTP protocol requests. Stream load synchronously executes the import and returns the import result. Users can directly determine whether the import is successful by the return body of the request. Stream load is mainly suitable for importing local files or data from data streams through procedures.

Each import job of Doris, whether it is batch import using Stream Load or single import using INSERT statement, is a complete transaction operation. The import transaction can ensure that the data in a batch takes effect atomically, and there will be no partial data writing.
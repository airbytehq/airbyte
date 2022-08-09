# Setup of Airbyte:

## Purpose
We want to export data from a variety of systems into a [Data Warehouse](https://en.wikipedia.org/wiki/Data_warehouse) in order to be able to
perform analytics on the data we collect.
For a ```Data Warehouse``` we use [BigQuery](https://cloud.google.com/bigquery).

## Setup
Initially I was using a docker image of ```Airbyte``` and set it up on my Laptop.
I was using a ```Docker``` image of ```Airbyte``` available [here](https://docs.airbyte.com/quickstart/deploy-airbyte)
Check [airbyte-with-primetric](https://github.com/andrzejdackiewicz/airbyte-with-primetric.git) if You want to use
```Airbyte``` with a custom source ```Primetric``` connector.

## Sources
- [Harvest](https://www.getharvest.com/)
- [Primetric](https://www.primetric.com/)
- [BambooHR](https://www.bamboohr.com/)
- [Google Sheets](https://www.google.com/sheets/about/)

### Source Harvest

There is an out of the box definition of a [Harvest Source Connector](https://docs.airbyte.com/integrations/sources/harvest).
For authentication we will be using a ```Personal Account Token```.
We can generate one [here](https://id.getharvest.com/developers).

We need:
- ```Name``` For example ```Harvest-source-connector```
- ```Account ID```
- ```Start Date``` (we can use 2017-01-01T00:00:00Z as the beginning of logs, our logs start later)
- ```Authentication mechanism``` we choose ```Authenticate with Personal Account Token```
- ```Personal Account Token``` that we generated in ```Harvest```.

We Save changes and test the ```Source Connector``` everything should be fine.

### Source Primetric

There were no available out of the box definitions of a ```Source Connector``` for ```Primetric```.
I needed to created a ```Custom Connector``` according to [this](https://docs.airbyte.com/connector-development/tutorials/building-a-python-source/) instruction.
The ```Airbyte``` image with an additional definition is [here](https://github.com/andrzejdackiewicz/airbyte-with-primetric.git).

We need:
- ```Client Secret```
- ```Client ID```

### Source BambooHR

There is an out of the box definition of a [BambooHR Source Connector](https://docs.airbyte.com/integrations/sources/bamboo-hr/).

We need:
- ```An api permission``` We can manage those here:
  ```https://getindata.bamboohr.com/settings/permissions/```

- ```ApiKey``` should be generated while creating a permission.

### Source Google Sheets

There is an out of the box definition of a [Google Sheets Source Connector](https://docs.airbyte.com/integrations/sources/google-sheets).

For ```Airbyte``` to be able to use ```Google Sheets``` we need a Service Account that has access to specified sheets.
In ```GCP``` create a ```Service Account```, share sheets with email generated for a ```Service Account``` and generate a
JSON key for the ```Service Account```. The minimal role given to ```Service Account``` for a sheet should be ```Viewer```.
When we create a source connection we will use generated JSON and the link to the ```Google Sheet``` with the data that we want to export to ```BigQuery```.

## Destinations

### Prerequsites

Before we start defining ```Destinations``` on ```Airbyte```:

- We need to create a ```Service Account``` with the ability to create tables, write and alter data on
  GCP BigQuery.
- The ```Service Account``` needs to have a generated JSON key for authorization to ```BigQuery```.
  The same JSON can be used for all ```Destinations```.
- We create a separate [Dataset](https://cloud.google.com/bigquery/docs/datasets-intro) for each ```Source``` where the data can be written:
    - ```harvest-351907.harvest_airbyte_export```
    - ```harvest-351907.primetric_airbyte_export```
    - ```harvest-351907.bamboohr_airbyte_export```
    - ```harvest-351907.google_sheets_airbyte_export```

### Destination BigQuery

For each of the sources we create a ```Destination```:
- We click ```Destinations``` -> ```+ New destination```
- We choose ```BigQuery``` as the ```Destination type```
- We fill in the formulae:
    - ```Name```
    - ```ProjectID```
    - ```Dataset Location```
    - ```Default Dataset ID```
    - ```Service Account Key JSON``` - (here we use our generated JSON)

We click ```Set up destination``` and check if everything.

## Connections

We create a connection for each pair ```Source``` - ```Destination```. We should give it a name, select how often the sync should take place, select the streams that should be synced and the method of synchronization (overwrite / incremental / some other).
We choose whether we want just a raw data tables or do we want to use normalization. (We want to normalize everything apart from harvest-export as there is an error in Harvest source Normalization).

For ```Harvest``` connection click "+ Add transformation" and specify:
- ```Transformation name``` For example ```Harvest Custom Transformations```
- ```Custom DBT``` for ```Transformation type```
- ```fishtownanalytics/dbt:1.0.0``` for ```Docker image URL with dbt installed```
- ```run``` for ```Entrypoint arguments for dbt cli to run the project```
- ```https://github.com/andrzejdackiewicz/harvest-export-custom-transformation.git``` for ```Git repository URL of the custom transformation project```
- ```main``` for ```Git branch name```

Save configuration and set up connection. Everything should be good.

## Known issues and workarounds

### Running Airbyte on Kubernetes
The problem is described [here](https://github.com/airbytehq/airbyte/issues/5091).
It is currently not possible to use [Custom DBT Transformations](https://docs.airbyte.com/operator-guides/transformation-and-normalization/transformations-with-sql) for ```Airbyte``` running on ```Kubernetes```. For now we are using them
for exporting ```Harvest``` data. We need to have ```DBT Transformation``` because of the following issue with ```Harvest``` source connector.

If we can't use ```Kubernetes``` and want to deploy ```Airbyte``` somewhere then we can use a minimal (1 Core) VM instance on ```GCP Compute Engine```. and install
```Airbyte``` there. The data that is exported so far is very small in size and the exports do not take long. For cost optimization
we can also use preemptive VM and shut it down when not used.

### Normalization errors for Harvest source connector
There is a very well known problem with the [Harvest source connector](https://docs.airbyte.com/integrations/sources/harvest/).
The issue is described [here](https://github.com/airbytehq/airbyte/issues/11980).
During the sync there would be a problem with read data normalization before writing it to the table.
The workaround is to put data into BigQuery without normalization and use a [Custom DBT Transformation](https://docs.airbyte.com/operator-guides/transformation-and-normalization/transformations-with-sql).
I put my custom transformation [here](https://github.com/andrzejdackiewicz/harvest-export-custom-transformation.git). Use the main branch.
There is 1 simple transformation which reads data from a table with raw JSON format, normalizes it by putting read values into another table on BigQuery dataset.
```Airbyte``` uses the DBT project and uses it's transformations after writing raw data into BigQuery.

### No available connector for Primetric source
There was no available connector for ```Primetric```. That meant that we had to create a custom HTTP connector. I created a new connector following the [documentation](https://docs.airbyte.com/connector-development/tutorials/cdk-tutorial-python-http/getting-started).

The publically available ```Primetric Source Connector``` is [here](https://github.com/andrzejdackiewicz/airbyte-with-primetric.git).

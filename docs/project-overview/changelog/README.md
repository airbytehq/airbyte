# Changelog

## 06/24/2021 Summary

* New Source: [IBM Db2](../../integrations/sources/db2.md)
* 💎 We now support Avro and JSONL output for our S3 destination! 💎
* 💎 Brand new BigQuery destination flavor that now supports denormalized STRUCT types.
* ✨ Looker source now supports self-hosted instances.
* ✨ Facebook Marketing source is now migrated to the CDK, massively improving async job performance and error handling.

View the full connector release notes [here](./connectors.md).

As usual, thank you to some of our awesome community contributors this week: Harshith Mullapudi, Tyler DeLange, Daniel Mateus Pires, EdBizarro, Tyler Schroeder, and Konrad Schlatte!

## 06/18/2021 Summary

* New Source: [Snowflake](../../integrations/sources/snowflake.md)
* 💎 We now support custom dbt transformations! 💎
* ✨ We now support configuring your destination namespace at the table level when setting up a connection!
* ✨ The S3 destination now supports Minio S3 and Parquet output!

View the full release notes here: [Platform](./platform.md), [Connectors](./connectors.md)

As usual, thank you to some of our awesome community contributors this week: Tyler DeLange, Mario Molina, Rodrigo Parra, Prashanth Patali, Christopher Wu, Itai Admi, Fred Reimer, and Konrad Schlatte!

## 06/10/2021 Summary

* New Destination: [S3!!](../../integrations/destinations/s3.md) 
* New Sources: [Harvest](../../integrations/sources/harvest.md), [Amplitude](../../integrations/sources/amplitude.md), [Posthog](../../integrations/sources/posthog.md)
* 🐛 Ensure that logs from threads created by replication workers are added to the log file.
* 🐛 Handle TINYINT(1) and BOOLEAN correctly and fix target file comparison for MySQL CDC.
* Jira source: now supports all available entities in Jira Cloud.
* 📚 Added a troubleshooting section, a gradle cheatsheet, a reminder on what the reset button does, and a refresh on our docs best practices.

#### Connector Development:
* Containerized connector code generator
* Added JDBC source connector bootstrap template.
* Added Java destination generator.

View the full release notes highlights here: [Platform](./platform.md), [Connectors](./connectors.md)

As usual, thank you to some of our awesome community contributors this week (I've noticed that we've had more contributors to our docs, which we really appreciate).
Ping, Harshith Mullapudi, Michael Irvine, Matheus di Paula, jacqueskpoty and P.VAD.

## Overview

Airbyte is comprised of 2 parts:

* Platform (The scheduler, workers, api, web app, and the Airbyte protocol). Here is the [changelog for Platform](platform.md). 
* Connectors that run in Docker containers. Here is the [changelog for the connectors](connectors.md). 

## Airbyte Platform Releases

### Production v. Dev Releases

The "production" version of Airbyte is the version of the app specified in `.env`. With each production release, we update the version in the `.env` file. This version will always be available for download on DockerHub. It is the version of the app that runs when a user runs `docker-compose up`.

The "development" version of Airbyte is the head of master branch. It is the version of the app that runs when a user runs `docker-compose --env-file .env.dev -f docker-compose.yaml -f docker-compose.dev.yaml up`.

### Production Release Schedule

#### Scheduled Releases

Airbyte currently releases a new minor version of the application on a weekly basis. Generally this weekly release happens on Monday or Tuesday.

#### Hotfixes

Airbyte releases a new version whenever it discovers and fixes a bug that blocks any mission critical functionality.

**Mission Critical**

e.g. Non-ASCII characters break the Salesforce source.

**Non-Mission Critical**

e.g. Buttons in the UI are offset.

#### Unscheduled Releases

We will often release more frequently than the weekly cadence if we complete a feature that we know that a user is waiting on.

### Development Release Schedule

As soon as a feature is on master, it is part of the development version of Airbyte. We merge features as soon as they are ready to go \(have been code reviewed and tested\). We attempt to keep the development version of the app working all the time. We are iterating quickly, however, and there may be intermittent periods where the development version is broken.

If there is ever a feature that is only on the development version, and you need it on the production version, please let us know. We are very happy to do ad-hoc production releases if it unblocks a specific need for one of our users.

## Airbyte Connector Releases

Each connector is tracked with its own version. These versions are separate from the versions of Airbyte Platform. We generally will bump the version of a connector anytime we make a change to it. We rely on a large suite of tests to make sure that these changes do not cause regressions in our connectors.

When we updated the version of a connector, we usually update the connector's version in Airbyte Platform as well. Keep in mind that you might not see the updated version of that connector in the production version of Airbyte Platform until after a production release of Airbyte Platform.


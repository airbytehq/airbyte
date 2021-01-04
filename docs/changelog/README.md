# Changelog

## Airbyte Core Releases

Airbyte Core is any non-connector code. This includes the scheduler, workers, api, web app, and the Airbyte protocol.

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

Each connector is tracked with its own version. These versions are separate from the versions of Airbyte Core. We generally will bump the version of a connector anytime we make a change to it. We rely on a large suite of tests to make sure that these changes do not cause regressions in our connectors.

When we updated the version of a connector, we usually update the connector's version in Airbyte Core as well. Keep in mind that you might not see the updated version of that connector in the production version of Airbyte Core until after a production release of Airbyte Core.


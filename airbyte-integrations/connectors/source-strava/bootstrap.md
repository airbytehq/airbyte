## Core streams

Strava is a REST based API. Connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

Connector supports the following two streams:
* [Athlete Stats](https://developers.strava.com/docs/reference/#api-Athletes-getStats)
    * Returns a set of stats specific to the specified `athlete_id` config input
* [Activities](https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities) \(Incremental\)
    * Returns activities of the athlete whose refresh token it belongs to
    * Stream will start with activities that happen after the `started_at` config input
    * Stream will keep on attempting to read the next page of query until the API returns an empty list

Rate Limiting:
* Strava API has limitations to 100 requests every 15 minutes, 1000 daily

Authentication and Permissions:
* Streams utilize [Oauth](https://developers.strava.com/docs/authentication/#oauthoverview) for authorization
* The [Activities](https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities) stream relies on the refresh token containing the `activity:read_all` scope
* List of scopes can be found [here](https://developers.strava.com/docs/authentication/#detailsaboutrequestingaccess)
    * Scope of `activity:read` should work as well, but will not include private activities or privacy zone data


See [this](https://docs.airbyte.io/integrations/sources/strava) link for the nuances about the connector.

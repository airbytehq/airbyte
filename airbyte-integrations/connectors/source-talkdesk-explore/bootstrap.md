## Streams

Talkdesk Explore API is focused on delivering data reports, and this connector implements five streams:

* Calls Report
* User Status Report
* Studio Flow Execution Report
* Contacts Report
* Ring Attempts Report

Please refer to the official documentation for a list of all available reports: https://docs.talkdesk.com/docs/available-report

To request data from one of the endpoints, first you need to generate a report. This is done by a POST request where the payload is the report specifications. Then, the response will be a report ID that you need to use in a GET request to obtain the report's data.

This process is further explained here: [Executing a Report](https://docs.talkdesk.com/docs/executing-report)

## Pagination

To both report generation and report consumption, data is not paginated.

## Authentication

The only authentication method implemented so far is `Client Credentials`. You can read [here](https://docs.talkdesk.com/docs/authentication) about all the supported authentication methods.

# Zoom

## Overview

The Zoom source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

This Zoom source wraps the [Singer Zoom Tap](https://github.com/singer-io/tap-zoom).

### Output schema

Several output streams are available from this source:

* [Users](https://marketplace.zoom.us/docs/api-reference/zoom-api/users/users)
* [Meetings](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetings)
  * [Meeting Registrants](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingregistrants)
  * [Meeting Polls](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingpolls)
  * [Meeting Poll Results](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/listpastmeetingpolls)
  * [Meeting Questions](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingregistrantsquestionsget)
  * [Meeting Files](https://marketplace.zoom.us/docs/api-reference/zoom-api/deprecated-api-endpoints/listpastmeetingfiles)
* [Webinars](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinars)
  * [Webinar Panelists](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarpanelists)
  * [Webinar Registrants](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarregistrants)
  * [Webinar Absentees](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarabsentees)
  * [Webinar Polls](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarpolls)
  * [Webinar Poll Results](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/listpastwebinarpollresults)
  * [Webinar Questions](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarregistrantsquestionsget)
  * [Webinar Tracking Sources](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/gettrackingsources)
  * [Webinar Q&A Results](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/listpastwebinarqa)
  * [Webinar Files](https://marketplace.zoom.us/docs/api-reference/zoom-api/deprecated-api-endpoints/listpastwebinarfiles)
* [Report Meetings](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportmeetingdetails)
* [Report Meeting Participants](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportmeetingparticipants)
* [Report Webinars](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportwebinardetails)
* [Report Webinar Participants](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportwebinarparticipants)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Coming soon |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The connector is restricted by normal Zoom [requests limitation](https://marketplace.zoom.us/docs/api-reference/rate-limits#rate-limit-changes).

The Zoom connector should not run into Zoom API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Zoom JWT Token

### Setup guide

Please read [How to generate your JWT Token](https://marketplace.zoom.us/docs/guides/build/jwt-app).

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.2.4   | 2021-07-06 | [4539](https://github.com/airbytehq/airbyte/pull/4539) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |

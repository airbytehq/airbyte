# Contributing to source-zoom

## Deletions

Zoom's REST API exposes no deletion feed; deletions are only published as webhooks such as `meeting.deleted`.
Deleted meetings and webinars disappear from the next full refresh. For users, `users.status` (`active`,
`inactive`, or `pending`) is the only soft-delete indicator. Incremental streams do not observe deletions.

The authorization endpoint is hidden and defaults to Zoom's token URL.

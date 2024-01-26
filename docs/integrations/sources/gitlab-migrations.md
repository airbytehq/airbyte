# Gitlab Migration Guide

## Upgrading to 2.0.0


In the 2.0.0 config change, several streams were updated to date-time field format, as declared in the Gitlab API.
These changes impact `pipeline.created_at` and` pipeline.updated_at` fields for stream Deployments and `expires_at` field for stream Group Members and stream Project Members.
You will need to refresh the source schema and reset affected streams after upgrading.

## Upgrading to 2.2.0

In this release, merge_request_commits stream was fixed so now it returns commits for each found merge_request.
These changes leads to complete change of stream schema.
Users will need to refresh the source schema and reset merge_request_commits stream after upgrading.
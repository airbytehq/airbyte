# PostHog Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 introduces a single change to the `events` stream. It corrects the casting of the `event` field datatype, which was incorrectly labeled as a `json` object. Now, it is accurately attributed only as a `string`, as outlined in the PostHog [documentation](https://posthog.com/docs/api/events). To apply this change, refresh the schema for the 'events' stream and reset your data.

## Upgrading to 2.0.0
Version 2.0.0 introduces the a required parameter `project id` to the source configuration. You can find this in your project settings in posthog, or the in the URL. If your Posthog organisation has more than 1 project, a separate source is required for each project.

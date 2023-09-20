# Mixpanel

## Upgrading to 1.0.0
 In this release, the "datetime" column in the "engage" stream will transition from Date/Time/Datetime types to string due to Mixpanel inconsistencies, so you need to refresh schema. Additionally, the "credentials" field is now mandatory, and the "project_id" path has been updated, though a config migration will minimize disruptions.
# Linkedin Pages Migration Guide

## Upgrading to 2.0.0

- 2 new streams have been added which support time bound incremental sync. They need additional fields `start_date` and `time_granularity_type` to be defined in the config to work.
- For requesting API access for the created app, the Marketing Developer Platform API is no longer available and instead the Advertising API must be used. See [docs]("https://docs.airbyte.com/integrations/sources/linkedin-pages/") for more info.
# Linkedin Pages Migration Guide

## Upgrading to 1.0.7

- 2 new streams have been added which support time bound incremental sync. They need additional fields `start_date` and `time_granularity_type` to be defined in the config to work. `time_granularity_type` has a default value of `DAY` set, and `start_date` has a default value set 1 year prior to the current date.
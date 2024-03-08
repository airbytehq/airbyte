# SurveyMonkey Migration Guide

## Upgrading to 1.0.0

This update enhances the connector by integrating it with a low-code framework, improving its maintainability. 
However, it's important to note that this migration alters the state format of the `survey_responses` stream. 
Therefore, any connections utilizing the `survey_responses` stream in incremental mode will require resetting post-upgrade to prevent synchronization failures.

Also, the field value for `page_id` will no longer be present in records. If user use this field as a reference key, his relations filed should be updated manually in the DB. 

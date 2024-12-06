# Amazon Sqs Migration Guide

## Upgrading to 1.0.0

A major update of migrating the connector to low code with builder support.
Changes regarding configuration of spec:
- `access_key`, `secret_key`, `queue_url`, `region`, `target` are required for this connector to work
- Other specification parameters has default values which could be changed by user
- Delete messages after read is no longer supported as it is removed from the supported attributes of API request, Supported attributes reference - https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ReceiveMessage.html

New features:
- Support for builder with latest version
- Support for new action stream - GetQueueAttributes
- Users could experiments new action streams using the builder with local setup

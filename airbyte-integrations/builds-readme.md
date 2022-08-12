# How is the builds page generated? 
[This github action](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/connector_integration_tests.yml) runs once a day. 
It triggers builds for all connectors. The result of this build is persisted on an S3 bucket in our AWS dev environment. 
Ask for access rights from the Airbyte team if you need it to access the environment. This S3 bucket is hooked up to a CDN, AWS CloudFront. 
Then, [this Github action](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/build-report.yml) reads from Cloudfront to send a daily
Slack message informing us of the build status of any connectors in need of attention. 

# API Documentation Folder

- `generated-api-html`: Plain HTML file automatically generated from the Airbyte OAS spec as part of the build.
- `api-documentation.md`: Markdown for API documentation Gitbook [page](https://docs.airbyte.com/api-documentation).
- `rapidoc-api-docs.html`: HTML for actual API Spec Documentation and linked to in the above Gitbook page. This is a S3 static website hosted out of
  the [`airbyte-public-api-docs bucket`](https://s3.console.aws.amazon.com/s3/buckets/airbyte-public-api-docs?region=us-east-2&tab=objects) with a [Cloudfront Distribution](https://console.aws.amazon.com/cloudfront/home?#distribution-settings:E35VD0IIC8YUEW)
  for SSL. This file points to the Airbyte OAS spec on Master and will automatically mirror spec changes.
  This file will need to be uploaded to the `airbyte-public-api-docs` bucket for any file changes to propagate.

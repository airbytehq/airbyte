---
products: embedded
---

# Develop your app with Embedded

Once you've completed the [prerequisites and one-time setup](prerequisites-setup), begin developing your app. This article provides instructions on how to use and run the Node.js sample web app with the Embedded Widget.

## Fetch sample repo

Fetch the sample web app from GitHub.

```bash
git clone https://github.com/airbytehq/embedded-sampleweb-nodejs.git
```

## Set up .env

If you have completed it already during the prerequisites, create a .env file from the provided `.env.example`.

```bash
cd embedded-sampleweb-node.js
cp .env.example .env
```

Your .env should look similar to below. Substitute the placeholder values with those created during the prerequisites step.

```yaml
# Airbyte Embedded Configuration
## For security reasons, we require that the widget can only we attached to a specific origin.
## If you're developing locally, it will look like: http://localhost:3000
## Once you're in production, it will look like: https://app.abc.com
ALLOWED_ORIGIN=your_webapp_origin
## These 3 pieces of information are available in your initial workspace: Settings > Embedded
AIRBYTE_ORGANIZATION_ID=your_organization_id
AIRBYTE_CLIENT_ID=your_client_id
AIRBYTE_CLIENT_SECRET=your_client_secret

# AWS Credentials
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key

# S3 Configuration
S3_BUCKET=your_s3_bucket_name
S3_BUCKET_REGION=your_s3_bucket_region
S3_BUCKET_PREFIX=your_s3_bucket_prefix
```

## Install dependencies

Change directories to embedded-sampleweb-nodejs and run the following command.

```bash
npm build
```

## Configure allowed origin

To enable the app and Airbyte to communicate, please set `ALLOWED_ORIGIN` in the `.env` to the URL where you are running the sample web app. For example, if you are running the app on your local machine using the default configuration your `.env` entry is `ALLOWED_ORIGIN=http://localhost:3000`.

## Start server

Once you install dependencies successfully and configure your `.env`, start the app.

```bash
npm src/server.js
```

This starts both the server and web app. Open your browser to `http://localhost:300` to access the web interface.

![Web app home](https://github.com/airbytehq/embedded-sampleweb-nodejs/raw/main/homepage.png)

---
products: embedded
---

<head>
  <!-- HIDE PAGE FROM SEARCH ENGINES FOR NOW -->
  <meta name="robots" content="noindex, nofollow" />
</head>

# Airbyte Embedded

![Airbyte Embedded](./assets/embedded-overview.png)

[Airbyte Embedded](https://airbyte.com/ai) enables you to add hundreds of integrations into your product instantly. Your end-users can authenticate into their data sources and begin syncing data to your product. You no longer need to spend engineering cycles on data movement. Focus on what makes your product great, rather than maintaining ELT pipelines.

# Setup

## Prerequisites

1. Receive the following values from your Airbyte account representative. If you do not have one, [please reach out to our team](https://airbyte.com/company/talk-to-sales). Then, create an env file with the following:

```yaml
AIRBYTE_ORGANIZATION_ID=
AIRBYTE_CLIENT_ID=
AIRBYTE_CLIENT_SECRET=
EXTERNAL_USER_ID=
```

The `EXTERNAL_USER_ID` is a unique identifier you create and assign when generating an Embedded Widget. It is the identifier used to differentiate between unique users. You should create one unique identifier for each of your users. For testing, you may set `EXTERNAL_USER_ID=0`.

2. Configure or prepare an S3 bucket to load customer data to. Obtain the following values required to read from and write to the bucket to be used later during setup:

```yaml
AWS_S3_ACCESS_KEY_ID=
AWS_S3_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
S3_PATH_PREFIX=
S3_BUCKET_REGION=
```

## One-Time Setup

Before submitting requests to Airbyte, you’ll need to use your Client ID and Client Secret to generate the access key used for API request authentication. You can use the following [cURL to create an access key](https://reference.airbyte.com/reference/createaccesstoken#/):

```sh
curl --request POST \
     --url https://api.airbyte.com/v1/applications/token \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
      {
        "client_id": "<client_id>",
        "client_secret": "<client_secret>",
        "grant-type": "<client_credentials>"
      }'
```

Next, you’ll need to create a connection template. You only need to do this once. The template describes where your customer data will land, and at what frequency to sync customer data. By default, syncs will run every hour. Here’s an example cURL API request for creating an S3 destination using the values obtained earlier to connect to an S3 bucket:

```sh
curl --location --request POST 'https://api.airbyte.com/v1/config_templates/connections' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <token>' \
--data '{
    "destinationName": "destination-s3", 
    "organizationId": "<ORGANIZATION_ID>",
    "destinationActorDefinitionId": "4816b78f-1489-44c1-9060-4b19d5fa9362",
      "destinationConfiguration": {
        "access_key_id": "<AWS_S3_ACCESS_KEY_ID>",
        "secret_access_key": "<AWS_S3_SECRET_ACCESS_KEY>",
        "s3_bucket_name": "<S3_BUCKET_NAME>",
        "s3_bucket_path": "<S3_PATH_PREFIX>",
        "s3_bucket_region": "<S3_BUCKET_REGION>",
        "format": {
          "format_type": "JSONL"
          }
        }
      }
    }'
```

Once this succeeds, you are ready to send customer data through Airbyte.

## Developing your Application with Airbyte Embedded

We illustrate how to integrate Airbyte Embedded into your app with an example. Feel free to follow along with our example app, or use the steps as indications of what's needed to be implemented into your own codebase.

### JavaScript Project Prerequisites

1. Create a JavaScript project in a new `airbyte-embedded-demo` directory.

```sh
mkdir airbyte-embedded-demo
cd airbyte-embedded-demo 
npm init -y
```

2. Copy the `.env` file you previously created in the `airbyte-embedded-demo` directory.
3. Update your `package.json` with the following dependency:

```yaml
{
  "dependencies": {
      "express": "^5.1.0"
  }
}
```

### Frontend Application

Create an `index.html` file and paste in the following contents. This short webpage does a few things:
* It imports the Airbyte Embedded library.
* It requests the server for the Embedded token to be used by the Airbyte Embedded Library. This token is only valid for 15 minutes.
* It instantiates the widget with the access token, and renders a button.

<details>
<summary>index.html</summary>

```html
<!doctype html>
<html lang="en">
  <body>
    <button id="open-widget">Open Airbyte Embedded</button>

    <script src="https://cdn.jsdelivr.net/npm/@airbyte-embedded/airbyte-embedded-widget"></script>
    
    <script>
      document.getElementById('open-widget').addEventListener('click', async () => {
        try {
          const response = await fetch("http://localhost:3001/api/widget_token");
          const data = await response.json();

          const widget = new AirbyteEmbeddedWidget({
            token: data.token,
          });

          widget.open();
        } catch (err) {
          console.error("Failed to load widget:", err);
        }
      });
    </script>
  </body>
</html>
```

### Backend Server

Now, we outline step by step instructions for creating your `server.js` file. This server includes:
* Exchanging Airbyte Client ID and Client Secret for an API access token.
* Exchanging API access token in addition to metadata for an Airbyte Embedded token.
* Boilerplate for running an Express application with error handling.

You may follow step-by-step or jump to the end of this section for a full copy-pasteable example server to manage Airbyte Embedded.

Step-by-step creation of backend application:

1. Create your `server.js` file, import the express library and instantiate an app on port 3001.

```js
const express = require("express");

// Disable SSL verification for development
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware for parsing JSON requests
app.use(express.json());
```

2. Add CORS middleware so you browser accepts responses from the server.

```js
// Add CORS middleware
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  res.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");

  // Handle preflight requests
  if (req.method === "OPTIONS") {
    return res.sendStatus(200);
  }
  next();
});
```

3. Read from the `.env` file:

```js
// Read config from environment variables
const BASE_URL = process.env.BASE_URL || "https://api.airbyte.com";
const AIRBYTE_WIDGET_URL = `${BASE_URL}/v1/embedded/widget_token`;
const AIRBYTE_ACCESS_TOKEN_URL = `${BASE_URL}/v1/applications/token`;
const AIRBYTE_CLIENT_ID = process.env.AIRBYTE_CLIENT_ID;
const AIRBYTE_CLIENT_SECRET = process.env.AIRBYTE_CLIENT_SECRET;
const ORGANIZATION_ID = process.env.AIRBYTE_ORGANIZATION_ID;
const EXTERNAL_USER_ID = process.env.EXTERNAL_USER_ID;
```

</details>

4. Define an endpoint listening at `/api/widget_token`:

```js
app.get("/api/widget_token", async (req, res) => {
  try {
});
```

In the callback, submit a request to obtain an API access token:

```js
const access_token_body = JSON.stringify({
      client_id: AIRBYTE_CLIENT_ID,
      client_secret: AIRBYTE_CLIENT_SECRET,
      "grant-type": "client_credentials",
    });
    const response = await fetch(AIRBYTE_ACCESS_TOKEN_URL, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: access_token_body,
    });
```

Still in the callback, use the API access token in the response to request an Embedded token encoding your API access key and metadata.

```js
const widget_token_response = await fetch(AIRBYTE_WIDGET_URL, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${access_token}`,
  },
  body: JSON.stringify({
    organizationId: AIRBYTE_ORGANIZATION_ID,
    allowedOrigin: origin,
    externalUserId: EXTERNAL_USER_ID,
  }),
});

const access_token_response = await response.json();
const access_token = access_token_response.access_token;
```

5. Finally, start the express application.

```js
app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});

```

Here is the full `server.js` file for reference:

<details>
<summary>server.js</summary>

```js
const express = require("express");

// Disable SSL verification for development
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware for parsing JSON requests
app.use(express.json());

// Add CORS middleware
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  res.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");

  // Handle preflight requests
  if (req.method === "OPTIONS") {
    return res.sendStatus(200);
  }
  next();
});

// Read config from environment variables
const BASE_URL = process.env.BASE_URL || "https://api.airbyte.com";
const AIRBYTE_WIDGET_URL = `${BASE_URL}/v1/embedded/widget_token`;
const AIRBYTE_ACCESS_TOKEN_URL = `${BASE_URL}/v1/applications/token`;
const AIRBYTE_CLIENT_ID = process.env.AIRBYTE_CLIENT_ID;
const AIRBYTE_CLIENT_SECRET = process.env.AIRBYTE_CLIENT_SECRET;
const ORGANIZATION_ID = process.env.AIRBYTE_ORGANIZATION_ID;
const EXTERNAL_USER_ID = process.env.EXTERNAL_USER_ID;

// GET /api/widget → fetch widget token and return it
app.get("/api/widget_token", async (req, res) => {
  try {
    // Determine the allowed origin from the request
    const origin =
      req.headers.origin ||
      req.headers.referer?.replace(/\/$/, "") ||
      process.env.ALLOWED_ORIGIN ||
      "http://localhost:3000";

    const access_token_body = JSON.stringify({
      client_id: AIRBYTE_CLIENT_ID,
      client_secret: AIRBYTE_CLIENT_SECRET,
      "grant-type": "client_credentials",
    });
    const response = await fetch(AIRBYTE_ACCESS_TOKEN_URL, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: access_token_body,
    });

    const access_token_response = await response.json();
    const access_token = access_token_response.access_token;

    const widget_token_response = await fetch(AIRBYTE_WIDGET_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${access_token}`,
      },
      body: JSON.stringify({
        organizationId: ORGANIZATION_ID,
        allowedOrigin: origin,
        externalUserId: EXTERNAL_USER_ID,
      }),
    });
    }

    const widget_response = await widget_token_response.json();

    res.json({ token: widget_response.token });
  } catch (err) {
    console.error("Unexpected error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
);

app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
```

</details>

### Install and Run JavaScript Application

1. Run `npm install`
2. Start your backend server with `env $(cat .env | xargs) node server.js`
3. Sever your frontend with `npx serve .`

## Using Airbyte Embedded

Once in your application, open Airbyte’s integration widget to see a catalog of available integrations. Choose one, and authenticate. Do not worry - if you want to show your own integration tiles, we support this flow as well.

*Tip: If you do not have a source system available to you at this time, use source ‘Faker’.*

![Airbyte Embedded](./assets/embedded-widget.png)

Once you’ve configured your source, wait a few minutes, and you should see loaded data in a new file in your S3 destination. You are all done! If you’d like to see your pipelines from the Airbyte Operator UI, feel free to do so by logging in to [Airbyte Cloud](cloud.airbyte.com).
---
products: embedded
---

# Develop your app with Embedded

Once you've completed the [prerequisites and one-time setup](prerequisites-setup), begin developing your app. This article illustrates how to integrate Airbyte Embedded into your app with an example. Feel free to follow along with this example app, or use the steps as indications of what you need to implement into your own codebase.

## JavaScript project prerequisites

1. Create a JavaScript project in a new `airbyte-embedded-demo` directory.

    ```sh
    mkdir airbyte-embedded-demo
    cd airbyte-embedded-demo 
    npm init -y
    ```

2. Copy the `.env` file you previously created in the `airbyte-embedded-demo` directory.

3. Update your `package.json` with the following dependency:

    ```yaml title="package.json"
    {
        "dependencies": {
            "express": "^5.1.0"
        }
    }
    ```

## Frontend app

Create an `index.html` file and paste in the following contents. This short webpage does a few things:

- It imports the Airbyte Embedded library.
- It requests the server for the Embedded token to be used by the Airbyte Embedded Library. This token is only valid for 15 minutes.
- It instantiates the widget with the access token, and renders a button.

    ```html title="index.html"
    <!doctype html>
    <html lang="en">
    <body>
        <button id="open-widget">Open Airbyte Widget</button>
        <script src="https://cdn.jsdelivr.net/npm/@airbyte-embedded/airbyte-embedded-widget"></script>
        
        <script>
        document.getElementById('open-widget').addEventListener('click', async () => {
            const response = await fetch("http://localhost:3001/api/widget_token");
            const data = await response.json();

            const widget = new AirbyteEmbeddedWidget({
            token: data.token,
            });

            widget.open();
        });
        </script>
    </body>
    </html>
    ```

## Backend server

These are the step by step instructions to create your `server.js` file. This server includes:

- Exchanging Airbyte Client ID and Client Secret for an API access token.
- Exchanging API access token in addition to metadata for an Airbyte Embedded token.
- Boilerplate for running an Express app with error handling.

You may follow step-by-step or jump to the end of this section for a full copy-pasteable example server to manage Airbyte Embedded.

Step-by-step creation of backend app:

1. Create your `server.js` file, import the express library and instantiate an app on port 3001.

    ```js title="server.js"
    const express = require("express");
    const path = require("path");

    // Disable SSL verification for development
    process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

    const app = express();
    const PORT = process.env.PORT || 3001;

    // Middleware for parsing JSON requests
    app.use(express.json());
    ```

2. Read from the `.env` file:

    ```js title="server.js"
    // Read config from environment variables
    const BASE_URL = process.env.BASE_URL || "https://api.airbyte.com";
    const AIRBYTE_WIDGET_URL = `${BASE_URL}/v1/embedded/widget_token`;
    const AIRBYTE_ACCESS_TOKEN_URL = `${BASE_URL}/v1/applications/token`;
    const AIRBYTE_CLIENT_ID = process.env.AIRBYTE_CLIENT_ID;
    const AIRBYTE_CLIENT_SECRET = process.env.AIRBYTE_CLIENT_SECRET;
    const ORGANIZATION_ID = process.env.AIRBYTE_ORGANIZATION_ID;
    const EXTERNAL_USER_ID = process.env.EXTERNAL_USER_ID;
    const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN || "http://localhost:3000";
    ```

3. Add a route for the root path.

    ```js title="server.js"
    // Route for the root path
    app.get('/', (req, res) => {
        res.sendFile(path.join(__dirname, './index.html'));
    });
    ```

4. Define an endpoint listening at `/api/widget_token`:

    ```js title="server.js"
    app.get("/api/widget_token", async (req, res) => {
    });
    ```

    In the callback, submit a request to obtain an API access token:

    ```js title="server.js"
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
    ```

    Still in the callback, use the API access token in the response to request an Embedded token encoding your API access key and metadata.

    ```js title="server.js"
    // Determine the allowed origin from the request
    const origin =
        req.headers.origin ||
        req.headers.referer?.replace(/\/$/, "") ||
        ALLOWED_ORIGIN;

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

    const widget_response = await widget_token_response.json();

    res.json({ token: widget_response.token });
    ```

5. Finally, start the express app.

    ```js title="server.js"
    app.listen(PORT, () => {
    console.log(`Server listening on http://localhost:${PORT}`);
    });
    ```

Here is the full `server.js` file for reference:

<details>
<summary>server.js</summary>

```js title="server.js"
const express = require("express");
const path = require("path");

// Disable SSL verification for development
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware for parsing JSON requests
app.use(express.json());


// Read config from environment variables
const BASE_URL = process.env.BASE_URL || "https://api.airbyte.com";
const AIRBYTE_WIDGET_URL = `${BASE_URL}/v1/embedded/widget_token`;
const AIRBYTE_ACCESS_TOKEN_URL = `${BASE_URL}/v1/applications/token`;
const AIRBYTE_CLIENT_ID = process.env.AIRBYTE_CLIENT_ID;
const AIRBYTE_CLIENT_SECRET = process.env.AIRBYTE_CLIENT_SECRET;
const ORGANIZATION_ID = process.env.AIRBYTE_ORGANIZATION_ID;
const EXTERNAL_USER_ID = process.env.EXTERNAL_USER_ID;
const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN || "http://localhost:3000";

// Route for the root path
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, './index.html'));
});

// GET /api/widget → fetch widget token and return it
app.get("/api/widget_token", async (req, res) => {


  const access_token_body = JSON.stringify({
    client_id: AIRBYTE_CLIENT_ID,
    client_secret: AIRBYTE_CLIENT_SECRET,
    "grant-type": "client_credentials",
  });
  console.log(access_token_body);
  const response = await fetch(AIRBYTE_ACCESS_TOKEN_URL, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: access_token_body,
  });

  const access_token_response = await response.json();
  console.log(access_token_response);
  const access_token = access_token_response.access_token;

  // Determine the allowed origin from the request
  const origin =
    req.headers.origin ||
    req.headers.referer?.replace(/\/$/, "") ||
    ALLOWED_ORIGIN;

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

  const widget_response = await widget_token_response.json();

  res.json({ token: widget_response.token });
});

app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
```

</details>

## Install and run the JavaScript app

1. Run `npm install`
2. Start your backend server with `env $(cat .env | xargs) node server.js`
3. Serve your frontend with `npx serve .`

# Hubspot Test Configuration

This integration wraps the existing singer [tap-hubspot](https://github.com/singer-io/tap-hubspot). In order to test the Hubspot source, you will need api credentials, see the [docs](https://docs.airbyte.io/integrations/sources/hubspot) for details.

## Community Contributor

1. Create a file at `secrets/config.json` with one of the following two format:
    1. If using an api key:
        ```
        {
          "start_date": "2017-01-01T00:00:00Z",
          "credentials": {
            "api_key": "your hubspot api key"
          }
        }
        ```
   1. If using oauth:
       ```
        {
          "start_date": "2017-01-01T00:00:00Z",
          "credentials": {
            "redirect_uri": "<redirect uri>",
            "client_id": "<hubspot client id>",
            "client_secret": "<hubspot client secret>",
            "refresh_token": "<hubspot refresh token>",
          }
        }
       ```

## Airbyte Employee

1. Access the api key credentials in the `hubspot-integration-test-api-key` secret on Rippling under the `Engineering` folder
    1. If we ever need a new api key it can be found in settings -> integrations (under the account banner) -> api key
1. Access the oauth config in the `hubspot-integration-test-oauth-config` secret on Rippling under the `Engineering` folder
    1. If we ever need to regenerate the refresh token for auth follow these hubspot [instructions](https://developers.hubspot.com/docs/api/oauth-quickstart-guide). Going to lay out the process because it wasn't 100% clear in their docs.
    1. Make sure you create or have developer account. I had an account but it wasn't a developer account, which means I couldn't access the oauth info.
    1. To get to an app (which can be tricky to find) go here https://app.hubspot.com/developer/8665273/applications.
    1. Then either use the existing app or create a new one.
    1. Then basic info -> auth will get you the client_id and client_secret
    1. Then you need to get a refresh token.
    1. Put this url in a browser https://app.hubspot.com/oauth/authorize?scope=contacts%20social&redirect_uri=https://www.example.com/auth-callback&client_id=<client-id>.
    1. It will direct you to a page in hubspot. Before you hit authorized on the next page open the developer console network tab. Okay, now hit authorize.
    1. In the developer console search for example.com and in the url params for the http request example.com there will be a code `https://www.example.com/auth-callback?code=<code>`. Save that code somewhere (I will refer to it as code below).
    1. Use this javascript snipped to get the refresh token. In the response body will be a refresh token.
       ```
       var request = require("request");
       
       const formData = {
         grant_type: 'authorization_code',
         client_id: '<client-id>',
         client_secret: '<client-secret>',
         redirect_uri: 'https://www.example.com/auth-callback',
         code: '<code>'
       };
       
       request.post('https://api.hubapi.com/oauth/v1/token', { form: formData }, (err, data) => {
         console.log(data)
       })
       ```
   1. Finally! You have all the pieces you need to do oauth with hubspot (client_id, client_secret, and refresh_token).


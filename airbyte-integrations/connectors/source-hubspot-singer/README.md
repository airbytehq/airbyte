# Github Test Configuration

This integration wraps the existing singer [tap-github](https://github.com/singer-io/tap-github). In order to test the Github source, you will need an access_key key from github. You can generate one by logging into github and then creating a personal access token [here](https://github.com/settings/tokens).

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

1. Access the api key creds in the `hubspot-integration-test-api-key` secret on Rippling under the `Engineering` folder
    1. If we ever need a new api key it can be found in settings -> integrations (under the account banner) -> api key
1. Access the oauth config in the `hubspot-integration-test-oauth-config` secret on Rippling under the `Engineering` folder
    1. If we ever need to regenerate the refresh token for auth follow these hubspot [instructions](https://developers.hubspot.com/docs/api/oauth-quickstart-guide).
1. If you ever need to set


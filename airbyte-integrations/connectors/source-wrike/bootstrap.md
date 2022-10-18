# Wrike

The connector uses the v4 API documented here: https://developers.wrike.com/overview/ . It is
straightforward HTTP REST API with Bearer token authentication. 

## Generating access token

First get a Wrike account, you can get a trial here: Register for trial: https://www.wrike.com/free-trial/

To generate a token:

1. Navigate to the ‘API apps’ section.
2. Select the required application from the list.
3. Click ‘Configure’.
4. Click ‘Obtain token’ in the “Permanent access token” section.
5. You will see a pop-up with a warning about using the permanent token, and after confirming, you will be able to copy and paste it into a secure storage (Wrike will not display it again). If your permanent token gets lost, you should generate a new one.

Auth is done by TokenAuthenticator. 

## Implementation details

I wrote a longer blog post on the implementation details: https://medium.com/starschema-blog/extending-airbyte-creating-a-source-connector-for-wrike-8e6c1337365a

In a nutshell:
 * We use only GET methods, all endpoints are straightforward. We emit what we receive as HTTP response.
 * The `comments` endpoint is the only trick one: it allows only 7 days data to be retrieved once. Thus, the codes creates 7 days slices, starting from start replication date.
 * It uses cursor based pagination. If you provide the next_page_token then no other parameters needed, the API will assume all parameters from the first page.


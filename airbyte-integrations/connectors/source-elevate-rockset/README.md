# Elevate Rockset Source

This is the repository for the Elevate Rockset source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/elevate-rockset).


## Rockset API
For the purpose of this demo I had created a lambda called "games"

## Rockset API queries
![alt text](https://raw.githubusercontent.com/milind-soni/source-elevate-rockset/main/Screenshot%20from%202022-09-03%2005-38-56.png)


## streams.py
### Workspace and path functions
The Rockset Query Lambda Endpoint base URL looks like https://api.use1a1.rockset.com/v1/orgs/self/ws/commons/lambdas/games/tags/latest

where games is the name of the workspace or lambda created.

For the purpose of this demo we will be taking input, the workspace which is the lambda and the API key which will eventually trigger the execution of these query using the Airbyte Connector.

the path function inputs the name of the workspace into the base URL 

## source.py

### check_connection:
we will be testing if the input is valid and working correctly. we have two inputs, one is the name of the lambda key or the workspace and the other input is the API key.

Testing the connection by running 
```
python3 main.py check --config secrets/config.json

```
![Connection Successful](https://raw.githubusercontent.com/milind-soni/source-elevate-rockset/main/Screenshot%20from%202022-09-03%2019-57-03.png)

## schemas 
it contains the schemas for the output of the API

## Querying the API 

Created configured catalog to query the API records 
```
 python main.py read --config secrets/config.json --catalog sample_files/configured_catalog.json

```

![Querying API](https://raw.githubusercontent.com/milind-soni/source-elevate-rockset/main/Screenshot%20from%202022-09-04%2019-18-06.png)

##Setting Up connection and adding it to the Airbyte UI

![Setting up Connection](https://raw.githubusercontent.com/milind-soni/source-elevate-rockset/main/Screenshot%20from%202022-09-05%2015-59-05.png)

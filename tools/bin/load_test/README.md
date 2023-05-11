# Load Testing Airbyte

## Overview
To perform a stress test of an Airbyte deployment, the `load_test_airbyte.sh` shell script is useful to quickly and easily create many connections. 
This script creates a new E2E Test Source, E2E Test Destination, and a configurable number of connections in the indicated workspace.

## Instructions
From your top-level `/airbyte` directory, run the following to perform a load test: 

```
./tools/bin/load_test/load_test_airbyte.sh -W <workspace id> -C <num_connections>
```


By default, the script assumes that the Airbyte instance's server is accessible at `localhost:8001`. This is the default server location when
deploying Airbyte with `docker compose up`.

Additionally, the E2E Test Source created by the script will take 10 minutes to complete a sync by default.

These defaults can be overridden with flags. All available flags are described as follows:

```
  -h
    Display help
    
  -W <workspace id>
    Specify the workspace ID where new connectors and connections should be created.
    Required.

  -H <hostname>
    Specify the Airbyte API server hostname that the script should call to create new connectors and connections.
    Defaults to 'localhost'.

  -P <port>
    Specify the port for the Airbyte server.
    Defaults to '8001'.

  -X <header>
    Specify the X-Endpoint-API-UserInfo header value for API authentication. 
    For Google Cloud Endpoint authentication only.

  -C <count>
    Specify the number of connections that should be created by the script.
    Defaults to '1'.

  -T <minutes>
    Specify the time in minutes that each connection should sync for.
    Defaults to '10'.
```


### Load Testing on Kubernetes

To load test a deployment of Airbyte running on Kubernetes, you will need to set up port-forwarding to the `airbyte-server` deployment.
This can be accomplished with the following command:

```
kubectl port-forward deployment/airbyte-server -n ab 8001:8001
```

This will make the Airbyte server available at `localhost:8001`


### Authentication

If your deployment of Airbyte happens to use Google Cloud Endpoints for authentication, you can use the `-X` option to pass 
an `X-Endpoint-API-UserInfo` header value.


## Cleanup
The `load_test_airbyte.sh` script writes created IDs to files in the script's `/cleanup` directory. To delete resources that were created by the load
test script, you can run `cleanup_load_test.sh`, which reads IDs from the `/cleanup` directory and calls the Airbyte API to delete them.


### Cleanup Instructions
To run the cleanup script, from the top-level `airbyte` directory, run the following:

```
./tools/bin/load_test/cleanup_load_test.sh -W <workspace_id>
```

All available cleanup script flags are described as follows:

```
  -h
    Display help

  -W <workspace id>
    Specify the workspace ID from where connectors and connections should be deleted.
    Required.

  -H <hostname>
    Specify the Airbyte API server hostname that the script should call to delete connectors and connections.
    Defaults to 'localhost'.

  -P <port>
    Specify the port for the Airbyte server.
    Defaults to '8001'.

  -X <header>
    Specify the X-Endpoint-API-UserInfo header value for API authentication. 
    For Google Cloud Endpoint authentication only.
```

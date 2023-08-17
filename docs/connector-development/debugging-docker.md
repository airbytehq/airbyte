# Debugging Docker Containers
This guide will cover debugging **JVM docker containers** either started via Docker Compose or started by the
worker container, such as a Destination container. This guide will assume use of [IntelliJ Community edition](https://www.jetbrains.com/idea/),
however the steps could be applied to another IDE or debugger.

## Prerequisites
You should have the airbyte repo downloaded and should be able to [run the platform locally](https://docs.airbyte.com/deploying-airbyte/local-deployment).
Also, if you're on macOS you will need to follow the installation steps for [Docker Mac Connect](https://github.com/chipmk/docker-mac-net-connect).

## Connecting your debugger
This solution utilizes the environment variable `JAVA_TOOL_OPTIONS` which when set to a specific value allows us to connect our debugger. 
We will also be setting up a **Remote JVM Debug** run configuration in IntelliJ which uses the IP address or hostname to connect.

> **Note**
> The [Docker Mac Connect](https://github.com/chipmk/docker-mac-net-connect) tool is what makes it possible for macOS users to connect to a docker container
> by IP address.

### Docker Compose Extension
By default, the `docker compose` command will look for a `docker-compose.yaml` file in your directory and execute its instructions. However, you can 
provide multiple files to the `docker compose` command with the `-f` option. You can read more about how Docker compose combines or overrides values when
you provide multiple files [on Docker's Website](https://docs.docker.com/compose/extends/).

In the Airbyte repo, there is already another file `docker-compose.debug.yaml` which extends the `docker-compose.yaml` file. Our goal is to set the  
`JAVA_TOOL_OPTIONS` environment variable in the environment of the container we wish to debug. If you look at the `server` configuration under `services`
in the `docker-compose.debug.yaml` file, it should look like this:
```yaml
  server:
    environment:
      - JAVA_TOOL_OPTIONS=${DEBUG_SERVER_JAVA_OPTIONS}
```
What this is saying is: For the Service `server` add an environment variable `JAVA_TOOL_OPTIONS` with the value of the variable `DEBUG_SERVER_JAVA_OPTIONS`.
`DEBUG_SERVER_JAVA_OPTIONS` has no default value, so if we don't provide one, `JAVA_TOOL_OPTIONS` will be blank or empty. When running the `docker compose` command,
Docker will look to your local environment variables, to see if you have set a value for `DEBUG_SERVER_JAVA_OPTIONS` and copy that value. To set this value
you can either `export` the variable in your environment prior to running the `docker compose` command, or prepend the variable to the command. For our debugging purposes,
we want the value to be `-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=*:5005` so to connect our debugger to the `server` container, run the following:

```bash
DEBUG_SERVER_JAVA_OPTIONS="-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=*:5005" VERSION="dev" docker compose -f docker-compose.yaml -f docker-compose.debug.yaml up
```

> **Note**
> This command also passes in the `VERSION=dev` environment variable, which is recommended from the comments in the `docker-compose.debug.yaml`

### Connecting the Debugger
Now we need to connect our debugger. In IntelliJ, open `Edit Configurations...` from the run menu (Or search for `Edit Configurations` in the command palette).
Create a new *Remote JVM Debug* Run configuration. The `host` option defaults to `localhost` which if you're on Linux you can leave this unchanged. 
On a Mac however, you need to find the IP address of your container. **Make sure you've installed and started the [Docker Mac Connect](https://github.com/chipmk/docker-mac-net-connect)
service prior to running the `docker compose` command**. With your containers running, run the following command to easily fetch the IP addresses:

```bash
$ docker inspect $(docker ps -q ) --format='{{ printf "%-50s" .Name}} {{printf "%-50s" .Config.Image}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
/airbyte-proxy                                     airbyte/proxy:dev                                  172.18.0.10172.19.0.4
/airbyte-server                                    airbyte/server:dev                                 172.18.0.9
/airbyte-worker                                    airbyte/worker:dev                                 172.18.0.8
/airbyte-source                                    sha256:5eea76716a190d10fd866f5ac6498c8306382f55c6d910231d37a749ad305960 172.17.0.2
/airbyte-connector-builder-server                  airbyte/connector-builder-server:dev               172.18.0.6
/airbyte-webapp                                    airbyte/webapp:dev                                 172.18.0.7
/airbyte-cron                                      airbyte/cron:dev                                   172.18.0.5
/airbyte-temporal                                  airbyte/temporal:dev                               172.18.0.2
/airbyte-db                                        airbyte/db:dev                                     172.18.0.4172.19.0.3
/airbyte-temporal-ui                               temporalio/web:1.13.0                              172.18.0.3172.19.0.2
```
You should see an entry for `/airbyte-server` which is the container we've been targeting so copy its IP address (`172.18.0.9` in the example output above)
and replace `localhost` in your IntelliJ Run configuration with the IP address.

Save your Remote JVM Debug run configuration and run it with the debug option. You should now be able to place breakpoints in any code that is being executed by the 
`server` container. If you need to debug another container from the original `docker-compose.yaml` file, you could modify the `docker-compose.debug.yaml` file with a similar option.

### Debugging Containers Launched by the Worker container
The Airbyte platform launches some containers as needed at runtime, which are not defined in the `docker-compose.yaml` file. These containers are the source or destination
tasks, among other things. But if we can't pass environment variables to them through the `docker-compose.debug.yaml` file, then how can we set the
`JAVA_TOOL_OPTIONS` environment variable? Well, the answer is that we can *pass it through* the container which launches the other containers - the `worker` container.

For this example, lets say that we want to debug something that happens in the `destination-postgres` connector container. To follow along with this example, you will
need to have set up a connection which uses postgres as a destination, however if you want to use a different connector like `source-postgres`, `destination-bigquery`, etc. that's fine.

In the `docker-compose.debug.yaml` file you should see an entry for the `worker` service which looks like this
```yaml
  worker:
    environment:
      - DEBUG_CONTAINER_IMAGE=${DEBUG_CONTAINER_IMAGE}
      - DEBUG_CONTAINER_JAVA_OPTS=-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=*:5005
```
Similar to the previous debugging example, we want to pass an environment variable to the `docker compose` command. This time we're setting the 
`DEBUG_CONTAINER_IMAGE` environment variable to the name of the container we're targeting. For our example that is `destination-postgres` so run the command:
```bash
DEBUG_CONTAINER_IMAGE="destination-postgres:5005" VERSION="dev" docker compose -f docker-compose.yaml -f docker-compose.debug.yaml up
```
The `worker` container now has an environment variable `DEBUG_CONTAINER_IMAGE` with a value of `destination-postgres` which when it compares when it is
spawning containers. If the container name matches the environment variable, it will set the `JAVA_TOOL_OPTIONS` environment variable in the container to
the value of its `DEBUG_CONTAINER_JAVA_OPTS` environment variable, which is the same value we used in the `server` example.

#### Connecting the Debugger to a Worker Spawned Container
To connect your debugger, **the container must be running**. This `destination-postgres` container will only run when we're running one of its tasks, 
such as when a replication is running. Navigate to a connection in your local Airbyte instance at http://localhost:8000 which uses postgres as a destination.
If you ran through the [Postgres to Postgres replication tutorial](https://airbyte.com/tutorials/postgres-replication), you can use this connection.

On the connection page, trigger a manual sync with the "Sync now" button. Because we set the `suspend` option to `y` in our `JAVA_TOOL_OPTIONS` the 
container will pause all execution until the debugger is connected. This can be very useful for methods which run very quickly, such as the Check method.
However, this could be very detrimental if it were pushed into a production environment. For now, it gives us time to set a new Remote JVM Debug Configuraiton. 

This container will have a different IP than the `server` Remote JVM Debug Run configuration we set up earlier. So lets set up a new one with the IP of 
the `destination-postgres` container:

```bash
$ docker inspect $(docker ps -q ) --format='{{ printf "%-50s" .Name}} {{printf "%-50s" .Config.Image}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
/destination-postgres-write-52-0-grbsw             airbyte/destination-postgres:0.3.26                
/airbyte-proxy                                     airbyte/proxy:dev                                  172.18.0.10172.19.0.4
/airbyte-worker                                    airbyte/worker:dev                                 172.18.0.8
/airbyte-server                                    airbyte/server:dev                                 172.18.0.9
/airbyte-destination                               postgres                                           172.17.0.3
/airbyte-source                                    sha256:5eea76716a190d10fd866f5ac6498c8306382f55c6d910231d37a749ad305960 172.17.0.2
/airbyte-connector-builder-server                  airbyte/connector-builder-server:dev               172.18.0.6
/airbyte-webapp                                    airbyte/webapp:dev                                 172.18.0.7
/airbyte-cron                                      airbyte/cron:dev                                   172.18.0.5
/airbyte-temporal                                  airbyte/temporal:dev                               172.18.0.3
/airbyte-db                                        airbyte/db:dev                                     172.18.0.2172.19.0.3
/airbyte-temporal-ui                               temporalio/web:1.13.0                              172.18.0.4172.19.0.2
```

Huh? No IP address, weird. Interestingly enough, all the IPs are sequential but there is one missing, `172.18.0.1`. If we attempt to use that IP in remote debugger, it works!

You can now add breakpoints and debug any code which would be executed in the `destination-postgres` container.

Happy Debugging!

#### Connecting the Debugger to an Integration Test Spawned Container
You can also debug code contained in containers spawned in an integration test! This can be used to debug integration tests as well as testing code changes. 
The steps involved are: 
1. Follow all the steps outlined above to set up the **Remote JVM Debug** run configuration.
2. Edit the run configurations associated with the given integration test with the following environment variables:`DEBUG_CONTAINER_IMAGE=source-postgres;DEBUG_CONTAINER_JAVA_OPTS=-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=*:5005`
Note that you will have to keep repeating this step for every new integration test run configuration you create. 
3. Run the integration test in debug mode. In the debug tab, open up the Remote JVM Debugger run configuration you just created. 
4. Keep trying to attach the Remote JVM Debugger. It will likely fail a couple of times and eventually connect to the test container. If you want a more
deterministic way to connect the debugger, you can set a break point in the `DockerProcessFactor.localDebuggingOptions()` method. Resume running the integration test run and
then attempt to attach the Remote JVM Debugger (you still might need a couple of tries).


## Gotchas
So now that your debugger is set up, what else is there to know?

### Code changes
When you're debugging, you might want to make a code change. Anytime you make a code change, your code will become out of sync with the container which is run by the platform.
Essentially this means that after you've made a change you will need to rebuild the docker container you're debugging. Additionally, for the connector containers, you may have to navigate to
"Settings" in your local Airbyte Platform's web UI and change the version of the container to `dev`. See you connector's `README` for details on how to rebuild the container image.

### Ports
In this tutorial we've been using port `5005` for all debugging. It's the default, so we haven't changed it. If you need to debug *multiple* containers however, they will clash on this port.
If you need to do this, you will have to modify your setup to use another port that is not in use.

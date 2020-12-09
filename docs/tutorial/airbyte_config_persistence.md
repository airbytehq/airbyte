---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.7.1
  kernelspec:
    display_name: Bash
    language: bash
    name: bash
---

# Airbyte Configuration Persistence Tutorial

Once you manage to spin up a local instance of Airbyte, following steps in the [Getting started Tutorial](../getting-started-tutorial.md), you may want to gain a better understanding of what configuration files are available in Airbyte and how to work with it.

This tutorial will go over importing and exporting Airbyte configurations of connectors which may be useful if you need for example to version control, share with your team or if you just want to debug things.

Here are the goals for this tutorial:
1. Access to replication logs files 
2. Export & Import Airbyte Configuration data files
3. Export normalization models to use in your own DBT project


```bash
# ignore this. Setup for Jupyter notebook

AIRBYTE_DIR=~/Workspace/airbyte
TUTORIAL_DIR=$(PWD)/build/persistence-tutorial
mkdir -p $TUTORIAL_DIR
cd $AIRBYTE_DIR
```

## Setting up a local Postgres Destination

For this tutorial, we are going to use 2 types of destinations to run our demo where data will be written:
- Local File Destination
- Local Postgres Database

The local files will be written to the directory `/tmp/airbyte_local`.

The postgres database that we are going to spin up below will be running locally with the following configuration where data will be written:

```text
Host: localhost
Port: 3000
User: postgres
Password: password
DB Name: postgres
```

```bash
echo "File Content in the local destination (may not exist yet):"
find /tmp/airbyte_local

echo ""

docker ps | grep -q local-airbyte-postgres-destination
if [ $? -eq 0 ]; then
    echo "Postgres Database local-airbyte-postgres-destination is already up"
else 
    echo "Start a Postgres container named local-airbyte-postgres-destination"
    docker run --rm --name local-airbyte-postgres-destination -e POSTGRES_PASSWORD=password -p 3000:5432 -d postgres
fi

echo ""

echo "Docker Containers currently running:"

docker ps
```

## Starting Airbyte Server

As we've seen in the previous tutorial, we can spin up Airbyte instance after installing it:

```bash
# Check if airbyte is installed
docker-compose config &> /dev/null
if [ $? -ne 0 ]; then
    git clone https://github.com/airbytehq/airbyte.git
    cd airbyte
fi 

docker-compose up -d

echo -e "\n"

echo "Docker Containers currently running:"
docker ps
```

Note that if you already went through the previous tutorial or already used Airbyte in the past, you may not need to complete the Onboarding process this time.

Otherwise, please complete the different steps until you reach the Airbyte Dashboard page.

After a few seconds, the UI should be ready to go at http://localhost:8000/.

## Notes about running this tutorial on Mac OS

Note that the commands in this tutorial will vary greatly depending on if you are running a Mac OS or Linux Operation System.

Docker for Mac is not a real Docker host, now it actually runs a virtual machine behind the scenes and hides it from you to make things simpler. 
Simpler, unless you want to dig deeper... just like our current use case where we want to inspect the content of internal Docker volumes...

Here are some related links as references on accessing Docker Volumes on Mac OS:
- [Screen + tty in 2017 (deprecated?)](https://timonweb.com/docker/getting-path-and-accessing-persistent-volumes-in-docker-for-mac/)
- [Using Docker containers in 2019](https://stackoverflow.com/a/55648186)

From these discussions, we will be using on Mac OS either:
1. any docker container/image to browse the virtual filesystem by mounting the volume in order to access them, for example with [busybox](https://hub.docker.com/_/busybox)
2. or extract files from the volume by copying them onto the host with [Docker cp](https://docs.docker.com/engine/reference/commandline/cp/)

Therefore, below commands will provide both versions for Mac OS and Linux, you can run the appropriate ones depending on your machine!

## Export Initial Setup

Now let's first make a backup of the configuration state of your Airbyte instance by running the following commands.

```bash
mkdir -p $TUTORIAL_DIR/my-setup

docker cp airbyte-server:/data $TUTORIAL_DIR/my-setup
```

<!-- #region -->
## Configure some Exchange Rate source and File destination

Head back to http://localhost:8000/ and add more connectors. 
Here is an example of configuration from an API source:

![airbyte_config_persistence_api_source](./airbyte_config_persistence_1.png)

and a local file destination:

![airbyte_config_persistence_local_file](./airbyte_config_persistence_2.png)

## Run a Sync job

- once the source and destination are created
- the catalog and frequency can be configured
- then run the "Sync Now" button
- finally inspect logs in the UI

![airbyte_config_persistence_ui_logs](./airbyte_config_persistence_3.png)


## Exploring Logs folders

We can read from the lines reported in the logs the working directory that is being used to run the synchronization process from.

As an example in the previous run, it is being ran in `/tmp/workspace/4/0` and we notice the different docker commands being used internally are starting with:
```bash
docker run --rm -i -v airbyte_workspace:/data -v /tmp/airbyte_local:/local -w /data/4/0 --network host ...
```

From there, we can observe that Airbyte is using a docker named volume called `airbyte_workspace` that is mounted in the container at the location `/data`.

Following [Docker Volume documentation](https://docs.docker.com/storage/volumes/), we can inspect and manipulate persisted configuration data in these volumes.
For example, we can run any docker container/image to browse the content of this named volume by mounting it in a similar way, let's use the [busybox](https://hub.docker.com/_/busybox) image.

```bash
docker run -it --rm --volume airbyte_workspace:/data busybox
```

This will drop you into an `sh` shell to allow you to do what you want inside a BusyBox system from which we can browse the filesystem and accessing to logs files:

```bash
ls /data/4/0/
``` 

Which should output:

```
catalog.json                  normalize                     tap_config.json
logs.log                      singer_rendered_catalog.json  target_config.json
```

Or you can simply run:
<!-- #endregion -->

```bash
docker run -it --rm --volume airbyte_workspace:/data busybox ls /data/4/0
```

```bash
docker run -it --rm --volume airbyte_workspace:/data busybox cat /data/4/0/catalog.json 
```

## Check local data folder

Since the job completed successfully, a new file should be available in the special `/local/` directory in the container which is mounted from `/tmp/airbyte_local` on the host machine.

```bash
echo "In the container:"

docker run -it --rm -v /tmp/airbyte_local:/local busybox find /local

echo ""
echo "On the host:"

find /tmp/airbyte_local
```

## Backup Exchange Rate Source and Destination configurations

In the following steps, we will play with persistence of configurations so let's make a backup of our newly added connectors for now:

```bash
mkdir -p $TUTORIAL_DIR/exchange-rate-setup

docker cp airbyte-server:data $TUTORIAL_DIR/exchange-rate-setup
```

## Shutting down Airbyte server and clear previous configurations

Whenever you want to stop the Airbyte server, you can run: `docker-compose down`

From [docker documentation](https://docs.docker.com/compose/reference/down/)
```
This command stops containers and removes containers, networks, volumes, and images created by up.

By default, the only things removed are:

- Containers for services defined in the Compose file
- Networks defined in the networks section of the Compose file
- The default network, if one is used

Networks and volumes defined as external are never removed.

Anonymous volumes are not removed by default. However, as they don’t have a stable name, they will not be automatically mounted by a subsequent up. For data that needs to persist between updates, use host or named volumes.
```

So since Airbyte is using named volumes to store the configurations, if you run 
`docker-compose up` again, your connectors configurations from earlier steps will still be available.

Let's wipe our configurations on purpose and use the following option:

```
-v, --volumes           Remove named volumes declared in the `volumes`
                            section of the Compose file and anonymous volumes
                            attached to containers.
```

Note that the `/tmp/airbyte_local:/local` that we saw earlier is a [bind mount](https://docs.docker.com/storage/bind-mounts/) so data that was replicated locally won't be affected by the next command.

However it will get rid of the named volume workspace so all logs and generated files by Airbyte will be lost.

We can then run:

```bash
docker-compose down -v
docker-compose up -d
```

Wait a moment for the webserver to start and go refresh the page http://localhost:8000/.

We are prompted with the onboarding process again...

Let's ignore that step, close the page and go back to the notebook to import configurations from our initial setup instead.

## Restore our initial setup

We can play and restore files in the named docker volume `data` and thus retrieve files that were created from earlier:

```bash
docker cp $TUTORIAL_DIR/my-setup/data/config airbyte-server:data
```

Now refresh back the page http://localhost:8000/ again, wait a little bit for the server to pick up the freshly imported configurations...
Tada! We don't need to complete the onboarding process anymore! 
and we have the list of connectors that were created previously available again. Thus you can use this ability of export/import files from named volumes to share with others the configuration of your connectors.

Warning: and it will include credentials, so be careful too!

## Configure some Covid (data) source and Postgres destinations

Let's re-iterate the source and destination creation, this time, with a file accessible from a public API:

![airbyte_config_persistence_ui_logs](./airbyte_config_persistence_4.png)

And a local Postgres Database:

![airbyte_config_persistence_ui_logs](./airbyte_config_persistence_5.png)

After setting up the connectors, we can trigger the sync and study the logs:

![airbyte_config_persistence_ui_logs](./airbyte_config_persistence_6.png)


## Export and customize Normalization step with DBT

In the previous connector configuration, selected a Postgres Database destination and chose to enable the "Basic Normalization" option.

In Airbyte, data is written in destination in a JSON blob format in tables with suffix "_raw" as it is taking care of the `E` and `L` in `ELT`. 

The normalization option adds a last `T` transformation step that takes care of converting such JSON tables into flat tables. 
To do so, Airbyte is currently using [DBT](https://docs.getdbt.com/) to handle such tasks which can be manually triggered in the normalization container like this:

```bash
NORMALIZE_WORKSPACE=`docker run --rm -i -v airbyte_workspace:/data  busybox find /data -path "*normalize/models*" | sed -E "s;/data/([0-9]+/[0-9]+/)normalize/.*;\1;g" | sort | 
uniq | tail -n 1`

docker run --rm -i -v airbyte_workspace:/data -w /data/$NORMALIZE_WORKSPACE/normalize --network host --entrypoint /usr/local/bin/dbt airbyte/normalization debug --profiles-dir=. --project-dir=.
docker run --rm -i -v airbyte_workspace:/data -w /data/$NORMALIZE_WORKSPACE/normalize --network host --entrypoint /usr/local/bin/dbt airbyte/normalization run --profiles-dir=. --project-dir=.
```

As seen earlier, it is possible to browse the workspace folders and examine further logs if an error occurs.

In particular, we can also take a look at the DBT models generated by Airbyte and export them to the local host filesystem:

```bash
rm -rf $TUTORIAL_DIR/normalization-files
mkdir -p $TUTORIAL_DIR/normalization-files

docker cp airbyte-server:/tmp/workspace/$NORMALIZE_WORKSPACE/normalize/ $TUTORIAL_DIR/normalization-files

NORMALIZE_DIR=$TUTORIAL_DIR/normalization-files/normalize
cd $NORMALIZE_DIR
cat $NORMALIZE_DIR/models/generated/*.sql
```

If you have [dbt cli](https://docs.getdbt.com/dbt-cli/cli-overview/) installed on your machine, you can then view, edit, customize and run the dbt models in your project if you want to bypass the normalization steps generated by Airbyte!

```bash
dbt debug --profiles-dir=$NORMALIZE_DIR --project-dir=$NORMALIZE_DIR 
dbt deps --profiles-dir=$NORMALIZE_DIR --project-dir=$NORMALIZE_DIR
dbt run --profiles-dir=$NORMALIZE_DIR --project-dir=$NORMALIZE_DIR --full-refresh
```

```bash

```

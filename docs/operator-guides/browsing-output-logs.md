---
products: all
---

# Browsing logs

Airbyte records the full logs as a part of each sync. These logs can be used to understand the underlying operations Airbyte performs to read data from the source and write to the destination as a part of the [Airbyte Protocol](/understanding-airbyte/airbyte-protocol.md). The logs includes many details, including any errors that can be helpful when troubleshooting sync errors.

:::info
When using Airbyte Open Source, you can also access additional logs outside of the UI. This is useful if you need to browse the Docker volumes where extra output files of Airbyte server and workers are stored.
:::

To find the logs for a connection, navigate to a connection's `Job History` tab to see the latest syncs.

## View the logs in the UI

To open the logs in the UI, select the three grey dots next to a sync and select `View logs`. This will open our full screen in-app log viewer.

:::tip
If you are troubleshooting a sync error, you can search for `Error`, `Exception`, or `Fail` to find common errors.
:::

The in-app log viewer will only search for instances of the search term within that attempt. To search across all attempts, download the logs locally.

## Link to a sync job

To help others quickly find your job, copy the link to the logs to your clipboard, select the three grey dots next to a sync and select `Copy link to job`.

You can also access the link to a sync job from the in-app log viewer.

## Download the logs

To download a copy of the logs locally, select the three grey dots next to a sync and select `Download logs`.

You can also access the download log button from the in-app log viewer.

:::note
If a sync was completed across multiple attempts, downloading the logs will union all the logs for all attempts for that job.
:::

## Exploring Local Logs

<AppliesTo oss />

### Establish the folder directory

In the UI, you can discover the Attempt ID within the sync job. Most jobs will complete in the first attempt, so your folder directory will look like `/tmp/workspace/9/0`. If you sync job completes in multiple attempts, you'll need to define which attempt you're interested in, and note this. For example, for the third attempt, it will look like `/tmp/workspace/9/2/` .

### Understanding the Docker run commands

We can also read the different docker commands being used internally are starting with:

```text
docker run --rm -i -v airbyte_workspace:/data -v /tmp/airbyte_local:/local -w /data/9/2 --network host ...
```

From there, we can observe that Airbyte is calling the `-v` option to use a docker named volume called `airbyte_workspace` that is mounted in the container at the location `/data`.

Following [Docker Volume documentation](https://docs.docker.com/storage/volumes/), we can inspect and manipulate persisted configuration data in these volumes.

### Opening a Unix shell prompt to browse the Docker volume

For example, we can run any docker container/image to browse the content of this named volume by mounting it similarly. In the example below, the [busybox](https://hub.docker.com/_/busybox) image is used.

```text
docker run -it --rm --volume airbyte_workspace:/data busybox
```

This will drop you into an `sh` shell inside the docker container to allow you to do what you want inside a BusyBox system from which we can browse the filesystem and accessing to log files:

```text
ls /data/9/2/
```

Example Output:

```text
catalog.json
tap_config.json
logs.log
target_config.json
```

### Browsing from the host shell

Or, if you don't want to transfer to a shell prompt inside the docker image, you can run Shell commands using docker commands as a proxy:

```bash
docker run -it --rm --volume airbyte_workspace:/data busybox ls /data/9/2
```

Example Output:

```text
catalog.json                 singer_rendered_catalog.json
logs.log                     tap_config.json
normalize                    target_config.json
```

### Reading the content of the catalog.json file

For example, it is often useful to inspect the content of the [catalog](../understanding-airbyte/beginners-guide-to-catalog.md) file. You could do so by running a `cat` command:

```bash
docker run -it --rm --volume airbyte_workspace:/data busybox cat /data/9/2/catalog.json
```

Example Output:

```text
{"streams":[{"stream":{"name":"exchange_rate","json_schema":{"type":"object","properties":{"CHF":{"type":"number"},"HRK":{"type":"number"},"date":{"type":"string"},"MXN":{"type":"number"},"ZAR":{"type":"number"},"INR":{"type":"number"},"CNY":{"type":"number"},"THB":{"type":"number"},"NZD":{"type":"number"},"BRL":{"type":"number"}}},"supported_sync_modes":["full_refresh"],"default_cursor_field":[]},"sync_mode":"full_refresh","cursor_field":[]}]}
```

### Extract catalog.json file from docker volume

Or if you want to copy it out from the docker image onto your host machine:

```bash
docker cp airbyte-server:/tmp/workspace/9/2/catalog.json .
cat catalog.json
```

### Browsing on Kubernetes

If you are running on Kubernetes, use the following commands instead to browsing and copy the files to your local.

To browse, identify the pod you are interested in and exec into it. You will be presented with a terminal that will accept normal linux commands e.g ls.

```bash
kubectl exec -it <pod name> -n <namespace pod is in> -c main bash
e.g.
kubectl exec -it destination-bigquery-worker-3607-0-chlle  -n jobs  -c main bash
root@destination-bigquery-worker-3607-0-chlle:/config# ls
FINISHED_UPLOADING  destination_catalog.json  destination_config.json
```

To copy the file on to your local in order to preserve it's contents:

```bash
kubectl cp <namespace pods are in>/<normalisation-pod-name>:/config/destination_catalog.json ./catalog.json
e.g.
kubectl cp jobs/normalization-worker-3605-0-sxtox:/config/destination_catalog.json ./catalog.json
cat ./catalog.json
```

## CSV or JSON local Destinations: Check local data folder

If you setup a pipeline using one of the local File based destinations \(CSV or JSON\), Airbyte is writing the resulting files containing the data in the special `/local/` directory in the container. By default, this volume is mounted from `/tmp/airbyte_local` on the host machine. So you need to navigate to this [local folder](file:///tmp/airbyte_local/) on the filesystem of the machine running the Airbyte deployment to retrieve the local data files.

:::caution

Please make sure that Docker Desktop has access to `/tmp` (and `/private` on a MacOS, as /tmp has a symlink that points to /private. It will not work otherwise). You allow it with "File sharing" in `Settings -> Resources -> File sharing -> add the one or two above folder` and hit the "Apply & restart" button.

:::

Or, you can also run through docker commands as proxy:

```bash
#!/usr/bin/env bash

echo "In the container:"

docker run -it --rm -v /tmp/airbyte_local:/local busybox find /local

echo ""
echo "On the host:"

find /tmp/airbyte_local
```

Example Output:

```text
In the container:
/local
/local/data
/local/data/exchange_rate_raw.csv

On the host:
/tmp/airbyte_local
/tmp/airbyte_local/data
/tmp/airbyte_local/data/exchange_rate_raw.csv
```

## Notes about running on macOS vs Linux

Note that Docker for Mac is not a real Docker host, now it actually runs a virtual machine behind the scenes and hides it from you to make things "simpler".

Here are some related links as references on accessing Docker Volumes:

- on macOS [Using Docker containers in 2019](https://stackoverflow.com/a/55648186)
- official doc [Use Volume](https://docs.docker.com/storage/volumes/#backup-restore-or-migrate-data-volumes)

From these discussions, we've been using on macOS either:

1. any docker container/image to browse the virtual filesystem by mounting the volume in order to access them, for example with [busybox](https://hub.docker.com/_/busybox)
2. or extract files from the volume by copying them onto the host with [Docker cp](https://docs.docker.com/engine/reference/commandline/cp/)

However, as a side remark on Linux, accessing to named Docker Volume can be easier since you simply need to:

```text
docker volume inspect <volume_name>
```

Then look at the `Mountpoint` value, this is where the volume is actually stored in the host filesystem and you can directly retrieve files directly from that folder.

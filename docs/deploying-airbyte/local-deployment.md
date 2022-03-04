# Local Deployment

{% hint style="info" %}
These instructions have been tested on MacOS, Windows 10 and Ubuntu 20.04.
{% endhint %}

## Setup & launch Airbyte

* Install Docker on your workstation \(see [instructions](https://www.docker.com/products/docker-desktop)\). Make sure you're on the latest version of `docker-compose`.
* After Docker is installed, you can immediately get started locally by running:

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

{% hint style="info" %}
If you're using Mac M1 \(Apple Silicon\) machines, you can run Airbyte locally only in `dev` mode and you need to set these environment variables in order to build Airbyte:

```bash
export DOCKER_BUILD_PLATFORM=linux/arm64
export DOCKER_BUILD_ARCH=arm64
export ALPINE_IMAGE=arm64v8/alpine:3.14
export POSTGRES_IMAGE=arm64v8/postgres:13-alpine
export JDK_VERSION=17
```

after setting up the environment variables you can start Airbyte locally by running:
```bash
VERSION=dev docker-compose up
```

{% endhint %}

* In your browser, just visit [http://localhost:8000](http://localhost:8000)
* Start moving some data!

## Deploy on Windows

We recommend following [this guide](https://docs.docker.com/docker-for-windows/install/) to install Docker on Windows. After installing the WSL 2 backend and Docker you should be able to run containers using Windows PowerShell. Additionally, as we note frequently, you will need `docker-compose` to build Airbyte from source. The suggested guide already installs `docker-compose` on Windows.

## Troubleshooting

**I have a Mac with the M1 chip. Is it possible to run Airbyte?**

Yes, you can run Airbyte in dev mode on Macs with M1 chip (see the note above). Some users using Macs with an M1 chip are facing some problems running Airbyte. The problem is related with the chip and Docker. [Issue \#2017](https://github.com/airbytehq/airbyte/issues/2017) was created to follow up the problem, you can subscribe to it and get updates about the resolution. If you can successfully run Airbyte using a MacBook with the M1 chip, let us know so that we can share the process with the community!

**Other issues**

If you encounter any issues, just connect to our [Slack](https://slack.airbyte.io). Our community will help! We also have a [troubleshooting](../troubleshooting/on-deploying.md) section in our docs for common problems.


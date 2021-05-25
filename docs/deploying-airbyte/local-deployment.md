# Local Deployment

{% hint style="info" %}
These instructions have been tested on MacOS, Windows 10 and Ubuntu 20.04.
{% endhint %}

## Setup & launch Airbyte

* Install Docker on your workstation \(see [instructions](https://www.docker.com/products/docker-desktop)\). Note: There is a known issue with docker-compose 1.27.3. If you are using that version, please upgrade to 1.27.4.
* After Docker is installed, you can immediately get started locally by running:

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

* In your browser, just visit [http://localhost:8000](http://localhost:8000)
* Start moving some data!

## Deploy on Windows

We recommend following [this guide](https://docs.docker.com/docker-for-windows/install/) to install Docker on Windows. After installing the WSL 2 backend and Docker you should be able to run containers using Windows PowerShell. Additionally, as we note frequently, you will need `docker-compose` to build Airbyte from source. The suggested guide already installs `docker-compose` on Windows. 

Instead of cloning the repo, you can alternatively download the latest Airbyte release [here](https://github.com/airbytehq/airbyte/releases). Unzip the downloaded file, access the unzipped file using PowerShell terminal, and run `docker-compose up`. After this, you should see the Airbyte containers in the Docker application as in the image below.

![](../.gitbook/assets/airbyte_deploy_windows_docker.png)

## Troubleshooting

**I have a Mac with the M1 chip. Is it possible to run Airbyte?**

Some users using Macs with an M1 chip are facing some problems running Airbyte.
The problem is related with the chip and Docker.  We're following the problem on this [issue](https://github.com/airbytehq/airbyte/issues/2017).
If you can run Airbyte using Apple MacBook with the M1 chip, let us know, the community will appreciate it.

**Other issues**

If you encounter any issues, just connect to our [Slack](https://slack.airbyte.io). Our community will help! We also have a [FAQ](../faq/technical-support.md) section in our docs for common problems.


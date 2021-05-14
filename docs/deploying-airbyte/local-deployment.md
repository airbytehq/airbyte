# Local Deployment

{% hint style="info" %}
These instructions have been tested on MacOS
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

We recommend follow [this](https://docs.docker.com/docker-for-windows/install/) steps to install Docker on Windows.
After installing WSL 2 backend and `docker` you should be able to run containers using Windows PowerShell. 
The steps on documentation suggested already install `docker-compose`. 
If you don't have `git` installed in your machine you can download the latest Airbyte release [here](https://github.com/airbytehq/airbyte/releases).
Unzip the file downloaded, access the path you unzip the file using PowerShell terminal and run `docker-compose up`.
After this, you should see the Airbyte containers in the Docker application as in the image below.
![](../.gitbook/assets/airbyte_deploy_windows_docker.png)

## Troubleshooting

If you encounter any issues, just connect to our [Slack](https://slack.airbyte.io). Our community will help! We also have a [FAQ](../faq/technical-support.md) section in our docs for common problems.


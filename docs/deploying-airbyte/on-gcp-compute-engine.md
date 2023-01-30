# Deploy Airbyte on GCP (Compute Engine)

This page guides you through deploying Airbyte Open Source on a [Google Cloud Platform (GCP) Compute Engine instance](https://cloud.google.com/compute/docs/instances) by setting up the deployment environment, installing and starting Airbyte, and connecting it to the GCP instance.

:::info

The instructions have been tested on a `Debian GNU/Linux 10` VM instance.

:::

## Requirements

- To test Airbyte, we recommend an `e2.medium` instance and provision at least 30GBs of disk per node
- To deploy Airbyte in a production environment, we recommend a `n1-standard-2` instance

## Set up the environment

1. Create a [new GCP instance](https://cloud.google.com/compute/docs/instances/create-start-instance).
2. Set variables in your local terminal:

```bash
PROJECT_ID=PROJECT_ID_WHERE_YOU_CREATED_YOUR_INSTANCE
INSTANCE_NAME=airbyte # or any other name that you've used
```

3. Install Google Cloud SDK and initialize the gcloud command-line tool using the following commands in your local terminal:

```bash
brew install --cask google-cloud-sdk
gcloud init
```

4. List all instances in your project and verify that you can see the Airbyte instance you created in step 1 in your local terminal:

```bash
# Verify you can see your instance
gcloud --project $PROJECT_ID compute instances list
[...] # You should see the airbyte instance you just created
```

5. Connect to your instance in your local terminal:

```bash
gcloud --project=$PROJECT_ID beta compute ssh $INSTANCE_NAME
```

6. Install Docker on your VM instance by following the below commands in your VM terminal:

```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add --
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian buster stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo usermod -a -G docker $USER
```

7. Install `docker-compose` on your VM instance by following the below commands in your VM terminal:

```bash
sudo apt-get -y install docker-compose-plugin
docker compose version
```

8.  Close the SSH connection on your VM instance to ensure the group modification is taken into account by following the below command in your VM terminal:

```bash
logout
```

## Install and launch Airbyte

To install and launch Airbyte:

1. In your local terminal, connect to your Google Cloud instance:

```bash
gcloud --project=$PROJECT_ID beta compute ssh $INSTANCE_NAME
```

2. In your VM terminal, install Airbyte:

```bash
mkdir airbyte && cd airbyte
curl -sOO https://raw.githubusercontent.com/airbytehq/airbyte/master/{.env,docker-compose.yaml}
docker compose up -d
```

## Connect to Airbyte

:::caution
For security reasons, we strongly recommended not exposing Airbyte publicly.
:::

1. In your local terminal, create an SSH tunnel to connect the GCP instance to Airbyte:

```bash
gcloud --project=$PROJECT_ID beta compute ssh $INSTANCE_NAME -- -L 8000:localhost:8000 -N -f
```

2. Verify the connection by visiting [http://localhost:8000](http://localhost:8000) in your browser.

## Troubleshooting

If you encounter any issues, reach out to our community on [Slack](https://slack.airbyte.com/).

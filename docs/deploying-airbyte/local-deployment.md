# Quickstart: Local Deployment

## Requirements
Airbyte only requires `docker` to be installed on the host, visit [Docker](https://docs.docker.com/get-docker/) for the installation instructions.

## Install & Run

To get started with Airbyte, just run:
```
curl -SsfL https://get.airbyte.com | bash -
```

This will install `abctl`, a very simple CLI to control your local Airbyte deployment. 

:::info
These instructions have been tested on most Linux distributions, MacOS, and Windows with WSL2.
:::

To start Airbyte, just run:
```
abctl local install --password "YOUR_PASSWORD"
```

:::info
Depending on how Docker is installed, you might need to use `sudo` :
```
sudo abctl local install --password "YOUR_PASSWORD"
```
:::

⏱️ Just wait a few minutes for Airbyte to get installed ⏱️.

At the end of the install you should have access to the Airbyte UI at: [`http://localhost:8000`](http://localhost:8000)

[Now let's just move some data](/using-airbyte/core-concepts)!

## Troubleshooting

If you have any questions about the local setup and deployment process, head over to our [Getting Started FAQ](https://github.com/airbytehq/airbyte/discussions/categories/questions) on our Airbyte Forum that answers the following questions and more:

- How long does it take to set up Airbyte?
- Where can I see my data once I've run a sync?
- Can I set a start time for my sync?

If you encounter any issues, check out [Getting Support](/community/getting-support) documentation
for options how to get in touch with the community or us.

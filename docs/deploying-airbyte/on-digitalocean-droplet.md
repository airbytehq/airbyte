# Deploy Airbyte on DigitalOcean

This page guides you through deploying Airbyte Open Source on a [DigitalOcean droplet](https://docs.digitalocean.com/products/droplets/how-to/create/) by setting up the deployment environment, and installing and starting Airbyte.  

Alternatively, you can deploy Airbyte on DigitalOcean in one click using their [marketplace](https://cloud.digitalocean.com/droplets/new?onboarding_origin=marketplace&appId=95451155&image=airbyte&utm_source=deploying-airbyte_on-digitalocean-droplet).

## Requirements

- To test Airbyte, we recommend a $20/month droplet
- To deploy Airbyte in a production environment, we recommend a $40/month instance

## Set up the Environment

To deploy Airbyte Open Source on DigitalOcean:

1. [Create a DigitalOcean droplet](https://docs.digitalocean.com/products/droplets/how-to/create/).
2. Connect to the droplet using the [Droplet Console](https://www.google.com/url?q=https://docs.digitalocean.com/products/droplets/how-to/connect-with-console/&sa=D&source=docs&ust=1666280581103312&usg=AOvVaw1hyEPyjRsmsRdIgbxZdu6F).
3. To update the available packages and install Docker, run the following command:

  ```bash
      sudo apt update
      sudo apt install apt-transport-https ca-certificates curl software-properties-common
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
      sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
      sudo apt install docker-ce
      sudo systemctl status docker
      sudo usermod -aG docker ${USER}
      su - ${USER}
  ```

4. To install Docker-Compose, run the following command:

```bash
    sudo apt install docker-compose-plugin
    docker compose version
```

## Install Airbyte

To install and start Airbyte :

1. Run the following command:

```bash
  mkdir airbyte && cd airbyte
  wget https://raw.githubusercontent.com/airbytehq/airbyte/master/{.env,docker-compose.yaml}
  docker compose up -d
```

2. Verify the connection by visiting [http://localhost:8000](http://localhost:8000) in your browser.

## Troubleshooting

If you encounter any issues, reach out to our community on [Slack](https://slack.airbyte.com/).  

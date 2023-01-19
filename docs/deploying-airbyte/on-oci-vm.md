# Deploy Airbyte on Oracle Cloud

This page guides you through deploying Airbyte Open Source on an [Oracle Cloud Infrastructure (OCI) Virtual Machine (VM) Instance](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/launchinginstance.htm#Creating_an_Instance).

:::info

These instructions have been tested on an Oracle Linux 7 instance.

:::

## Prerequisites 

To deploy Airbyte Open Source on Oracle cloud:

* Create an [OCI VM compute instance](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/launchinginstance.htm#Creating_an_Instance)
* Allowlist a port for a CIDR range in the [security list of your OCI VM Instance subnet](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/securitylists.htm)
* Connect to the instance using a [bastion port forwarding session](https://docs.oracle.com/en-us/iaas/Content/Bastion/Tasks/connectingtosessions.htm#connect-port-forwarding)

:::caution

For security reasons, we strongly recommend not having a Public IP for the Instance where you are running Airbyte.

:::

## Set up the environment

Install Docker and Docker Compose on the VM:

1. Install Docker

In the terminal connected to your OCI Instance for Airbyte, run the following commands:

```bash
sudo yum update -y

sudo yum install -y docker

sudo service docker start

sudo usermod -a -G docker $USER
```

2. Install Docker Compose

In the terminal connected to your OCI Instance for Airbyte, run the following commands:

```bash
sudo yum install -y docker-compose-plugin

docker compose version
```

## Install and start Airbyte

Download the Airbyte repository and deploy it on the VM:

1. Run the following commands to clone the Airbyte repo:

	```bash
	mkdir airbyte && cd airbyte

	wget https://raw.githubusercontent.com/airbytehq/airbyte/master/{.env,docker-compose.yaml}
	```

2. Run the following commands to get Airbyte running on your OCI VM instance using Docker compose:

    ```bash

    which docker

    sudo /usr/local/bin/docker compose up -d

    ``` 

3. Open up a Browser and visit port 8000 - [http://localhost:8000/](http://localhost:8000/)


Alternatively, you can get Airbyte running on your OCI VM instance using a different approach.

1. In the terminal connected to your OCI Instance for Airbyte, run the command: 

	```bash
	ssh opc@bastion-host-public-ip -i <private-key-file.key> -L 8000:oci-private-instance-ip:8000
	```

	Replace `<private-key-file.key>` with the path to your private key.

2. On your browser, visit port 8000 [port 8000](http://localhost:8000/)

## Troubleshooting

If you encounter any issues, reach out to our community on [Slack](https://slack.airbyte.com/).

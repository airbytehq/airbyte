# Deploy Airbyte on AWS (Amazon EC2)

This page guides you through deploying Airbyte Open Source on an [Amazon EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html) by setting up the deployment environment, installing and starting Airbyte, and connecting it to the Amazon EC2 instance.

:::info

The instructions have been tested on Amazon Linux 2 AMI (HVM).

:::

## Requirements

- To test Airbyte, we recommend a `t2.medium` instance
- To deploy Airbyte in a production environment, we recommend a `t2.large` instance
- Make sure your Docker Desktop app is running to ensure all services run smoothly
- [Create and download an SSH key to connect to the instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/create-key-pairs.html)

## Set up the environment

1. To connect to your instance, run the following command on your local terminal:

```bash
SSH_KEY=~/Downloads/dataline-key-airbyte.pem # the file path you downloaded the key
INSTANCE_IP=REPLACE_WITH_YOUR_INSTANCE_IP # find your IP address in the EC2 console under the Instances tab
chmod 400 $SSH_KEY # or ssh will complain that the key has the wrong permissions
ssh -i $SSH_KEY ec2-user@$INSTANCE_IP # connect to the aws ec2 instance AMI and the your private IP address
```

2. To install Docker, run the following command in your SSH session on the instance terminal:

```bash
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker $USER
```

3. To install `docker-compose`, run the following command in your ssh session on the instance terminal:

```bash
sudo yum install -y docker-compose-plugin
docker compose version
```

If you encounter an error on this part, you might prefer to follow the documentation to [install the docker compose plugin manually](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually) (_make sure to do it for all users_).

4. To close the SSH connection, run the following command in your SSH session on the instance terminal:

```bash
logout
```

## Install and start Airbyte

In your local terminal, run the following commands:

1. Connect to your instance:

```bash
ssh -i $SSH_KEY ec2-user@$INSTANCE_IP
```

2. Install Airbyte:

```bash
mkdir airbyte && cd airbyte
wget https://raw.githubusercontent.com/airbytehq/airbyte/master/run-ab-platform.sh
chmod +x run-ab-platform.sh
./run-ab-platform.sh -b
```

## Connect to Airbyte

:::caution

For security reasons, we strongly recommend not exposing Airbyte on Internet available ports.

:::

1. Create an SSH tunnel for port 8000:

If you want to use different ports, modify `API_URL` in your .env file and restart Airbyte.
Run the following commands in your workstation terminal from the downloaded key folder:

```bash
# In your workstation terminal
SSH_KEY=~/Downloads/dataline-key-airbyte.pem
ssh -i $SSH_KEY -L 8000:localhost:8000 -N -f ec2-user@$INSTANCE_IP
```

2. Visit `http://localhost:8000` to verify the deployment.

## Get Airbyte logs in CloudWatch

Follow this [guide](https://aws.amazon.com/en/premiumsupport/knowledge-center/cloudwatch-docker-container-logs-proxy/) to get your logs from your Airbyte Docker containers in CloudWatch.

## Troubleshooting

If you encounter any issues, reach out to our community on [Slack](https://slack.airbyte.com/).

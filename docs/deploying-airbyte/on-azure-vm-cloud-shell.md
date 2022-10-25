# Deploy on Azure 

This page guides you through deploying Airbyte Open Source on a Microsoft Azure VM by setting up the deployment environment, installing and starting Airbyte, and connecting it to the VM.

:::info

The instructions have been tested on a standard DS1 v2 (1 vcpu, 3.5 GiB memory) Microsoft Azure VM with Ubuntu 18.04.

:::

## Set up the environment

Install Docker and Docker Compose in the VM:

1. [Create a new VM](https://learn.microsoft.com/en-us/azure/virtual-machines/) and [generate the SSH keys](https://learn.microsoft.com/en-us/azure/virtual-machines/ssh-keys-portal) to connect to the VM. You’ll need the SSH keys to connect to the VM remotely later. 

2. To connect to the VM, run the following command in the Azure Cloud Shell:

    ```bash
    ssh <admin username>@<IP address>
    ```
    If successfully connected to the VM, the working directory of Cloud Shell should look like this: `<admin username>@<virtual machine name>:~$`

3. To install Docker, run the following commands:

    ```bash
    sudo apt-get update -y
    sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release -y
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli -y
    sudo usermod -a -G docker $USER
    ```

4. To install Docker Compose, run the following command:

    ```bash
    sudo wget https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m) -O /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ```

5. Check Docker Compose version:

    ```bash
    docker-compose --version
    ```

6. Close the SSH connection to ensure that the group modification is considered:

    ```bash
    logout
    ```

7. Reconnect to the VM:

    ```bash
    ssh <admin username>@<IP address>
    ```

## Install and start Airbyte

Download Airbyte and deploy it in the VM using Docker Compose:

1. Ensure that you are connected to the VM:

    ```bash
    ssh <admin username>@<IP address>
    ```

2. Create and use a new directory:

    ```bash 
    mkdir airbyte
    cd airbyte
    ```

3. Download Airbyte from GitHub: 

    ```bash
    wget https://raw.githubusercontent.com/airbytehq/airbyte/master/{.env,docker-compose.yaml}
    ```

4. Start Airbyte by running the following command:

    ```bash
    sudo docker-compose up -d
    ```
    This step takes about two minutes to complete. When done, you will see the cursor prompt.


## Connect to Airbyte

Test a remote connection to your VM locally and verify that Airbyte is up and running.

1. In your local machine, open a terminal. 
2. Go to the folder where you stored the SSH key.
3. Create a SSH tunnel for `port 8000` by typing the following command:

    ```bash 
    ssh -N -L 8000:localhost:8000 -i <your SSH key file> <admin username>@<IP address>
    ```
	As a result, nothing happens. The cursor prompt keeps blinking.

4. Open a web browser and navigate to `http://localhost:8000`. You will see Airbyte’s landing page. 

:::danger

For security reasons, it is strongly recommended not to expose Airbyte on Internet available ports. Future versions will add support for SSL and authentication.

:::

## Troubleshooting

If you encounter any issues, reach out to our community on [Slack](https://slack.airbyte.com/).
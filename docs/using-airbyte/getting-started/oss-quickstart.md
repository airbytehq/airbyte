---
products: oss-community
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Quickstart

This quickstart guides you through deploying a local instance of Airbyte Self-Managed Community, Airbyte's open source product. Setup only takes a few minutes, and you can start moving data on our platform immediately.

## Overview

This quickstart shows you how to:

- [Install abctl](#install-abctl)
- [Run Airbyte](#run-airbyte)
- [Set up authentication](#authentication)
- [Decide on your next steps](#next-steps)

This is intended for most people who want to manage their own Airbyte instance, but it assumes you have basic knowledge of:

- Docker
- Command-line tools

If you do not want to self-manage Airbyte, skip this guide. Sign up for an [Airbyte Cloud](https://cloud.airbyte.com/signup) trial and [start syncing data](add-a-source.md) now.

If you want to use Python to move data, our Python library, [PyAirbyte](../pyairbyte/getting-started.mdx), might be the best fit for you. It's a good choice if you're using Jupyter Notebook or iterating on an early prototype for a large data project and don't need to run a server.

## Before you start

Before running this quickstart, complete the following prerequisites:

1. Install Docker Desktop on your machine: [Mac](https://docs.docker.com/desktop/install/mac-install/), [Windows](https://docs.docker.com/desktop/install/windows-install/), [Linux](https://docs.docker.com/desktop/install/linux-install/).
2. Make sure you have enough computing power (see Suggested resources, below).

### Suggested resources {#suggested-resources}

For best performance, run Airbyte on a machine with 4 or more CPUs and at least 8GB of memory. We also support running Airbyte with 2 CPUs and 8GM of memory in low-resource mode. This guide explains how to do both. Follow this [Github discussion](https://github.com/airbytehq/airbyte/discussions/44391) to upvote and track progress toward supporting lower resource environments.

## Part 1: Install abctl

abctl is Airbyte's command-line tool for deploying and managing Airbyte. 

### Install abctl the fast way (Mac, Linux) <!-- I think Windows ships with cURL now - can we use it? -->

1. Open a terminal and run the following command.

    ```shell
    curl -LsfS https://get.airbyte.com | bash -
    ```

2. If your terminal asks you to enter your password, do so.

When installation completes, you'll see `abctl install succeeded.`

### Install abctl manually (Mac, Linux, Windows)

To install abctl yourself, follow the instructions for your operating system.

<Tabs defaultValue="abctl-mac">
<TabItem value="abctl-mac" label="Mac">

Use [Homebrew](https://brew.sh/) to install abctl.

1. Install Homebrew, if you haven't already.

2. Run the following commands after Homebrew is installed.

    ```bash
    brew tap airbytehq/tap
    brew install abctl
    ```

3. Keep abctl up to date with Homebrew, too.

    ```bash
    brew upgrade abctl
    ```

</TabItem>
<TabItem value="abctl-linux" label="Linux" default>

1. Verify your processor architecture.

    ```bash
    uname -m
    ```

    If the output is `x86_64`, you'll download the **linux-amd64** release. If the output is `aarch64` or similar, you'll download the **linux-arm64** release.

2. Download the file that is compatible with your machine's processor architecture

    <a class="abctl-download button button--primary" data-architecture="linux" href="https://github.com/airbytehq/abctl/releases/latest" target="_blank" download>Latest Linux Release</a>

3. Extract the archive. This creates a directory named `abctl`, which contains the executable and other needed files.

    ```bash
    tar -xvzf {name-of-file-downloaded.linux-*.tar.gz}
    ```

4. Make the extracted executable accessible. This allows you to run `abctl` as a command.

    ```bash
    chmod +x abctl/abctl
    ```

5. Add `abctl` to your PATH. This allows you to run `abctl` from any directory in your terminal.

    ```bash
    sudo mv abctl /usr/local/bin
    ```

6. Verify the installation. If this command prints the installed version of abctl, you can now use it to manage a local Airbyte instance.

```bash
abctl version
```

</TabItem>
<TabItem value="abctl-windows" label="Windows" default>

1. Verify your processor architecture.

    1. Press <kbd><svg xmlns="http://www.w3.org/2000/svg" height="10" width="8.75" viewBox="0 0 448 512"><path d="M0 93.7l183.6-25.3v177.4H0V93.7zm0 324.6l183.6 25.3V268.4H0v149.9zm203.8 28L448 480V268.4H203.8v177.9zm0-380.6v180.1H448V32L203.8 65.7z"/></svg></kbd> + <kbd>I</kbd>.

    2. Click **System** > **About**.

    3. Next to **Processor**, if it says `AMD`, you'll download the **windows-amd64** release. If the output is `ARM` or similar, you'll download the **windows-arm64** release.

2. Download the latest release of `abctl`.

    <a class="abctl-download button button--primary" data-architecture="windows" href="https://github.com/airbytehq/abctl/releases/latest" target="_blank" download>Latest Windows Release</a>

3. Extract the zip file to a destination of your choice. This creates a folder containing the abctl executable and other required files. Copy the filepath because you'll need this in a moment.

4. Add the executable to your `Path` environment variable.

    1. Click <svg xmlns="http://www.w3.org/2000/svg" height="10" width="8.75" viewBox="0 0 448 512"><path d="M0 93.7l183.6-25.3v177.4H0V93.7zm0 324.6l183.6 25.3V268.4H0v149.9zm203.8 28L448 480V268.4H203.8v177.9zm0-380.6v180.1H448V32L203.8 65.7z"/></svg> **Start** and type `environment`.

    2. Click **Edit the system environment variables**. The System Properties opens.

    3. Click **Environment Variables**.

    4. Find the Path variable and click **Edit**.

    5. Click **New**, then paste the filepath you saved in step 3.

    6. Click **OK**, then click **OK**, then close the System Properties.

5. Open a new Command Prompt or PowerShell window. Changes to your Path variable only take effect in a new Window.

6. Verify abctl is installed correctly. If this command prints the installed version of abctl, you can now use it to manage a local Airbyte instance.

    ```bash
    abctl version
    ```

</TabItem>
</Tabs>

## Part 2: Run Airbyte

1. Run Docker Desktop.

2. Install Airbyte.

    To run Airbyte with on a machine with the recommended resources (4 or more CPUs), use this command:

    ```bash
    abctl local install
    ```

    <!-- [[[This is good to know but I don't think it's within the scope of this guide.]]]
    To make Airbyte accessible outside `localhost`, specify the `--host` flag to the local install command, and provide a fully qualified domain name for Airbyte's host.

    ```bash
    abctl local install --host airbyte.example.com
    ``` 
    -->

    To run Airbyte in a low-resource environment (fewer than 4 CPUs), specify the `--low-resource-mode` flag to the local install command.

    ```bash
    abctl local install --low-resource-mode
    ```

Installation may take up to 15 minutes depending on your internet connection. When it completes, your Airbyte instance opens in your web browser at [http://localhost:8000](http://localhost:8000).

As long as your Docker Desktop daemon is running in the background, use Airbyte by returning to [http://localhost:8000](http://localhost:8000). If you quit Docker Desktop and want to return to Airbyte, start Docker Desktop again. Once your containers are running again, you can access Airbyte normally.

## Part 3: Set up authentication

To access your Airbyte instance, you need a password.

1. Get your default password.

    ```bash
    abctl local credentials
    ```

    This outputs something like this:

    ```shell
    Credentials:
    Email: user@company.example
    // highlight-next-line
    Password: random_password
    Client-Id: 03ef466c-5558-4ca5-856b-4960ba7c161b
    Client-Secret: m2UjnDO4iyBQ3IsRiy5GG3LaZWP6xs9I
    ```

    You can use that password to log into Airbyte, but you probably want to use your own email and password.

3. Set an email.

    ```bash
    abctl local credentials --email your.name@example.com
    ```

4. Set a new password.

    ```bash
    abctl local credentials --password YourStrongPasswordExample
    ```

Use this email and password to log into Airbyte in the future.

## What's next

Congratulations! You have a fully-functional instance of Airbyte running locally. Time to take Airbyte for a spin.

### Move data

In Airbyte, you move data from [sources](./add-a-source) to [destinations](./add-a-destination.md). The relationship between sources and destination is called a [connection](./set-up-a-connection.md). Try moving some data on your local instance!

### Deploy Airbyte

If you want to scale data movement in your organization, you eventually need to move Airbyte off your local machine. You can use a cloud provider like AWS, Google Cloud, or Azure. You can also use a single node like an AWS EC2 virtual machine. See the [deployment guide](../../deploying-airbyte/) to learn more.

## Uninstall Airbyte

To stop running all containers, but keep your data:

```shell
abctl local uninstall
```

To stop running containers and delete all data:

1. Uninstall Airbyte with the `--persisted` flag.

    ```shell
    abctl local uninstall --persisted
    ```

2. Clear any remaining information abctl created.

    ```shell
    rm -rf ~/.airbyte/abctl
    ```

<!-- [[[this info is probably not required anymore. Preserving here just in case.]]]

## Migrating from Docker Compose (Optional)

:::note

If you're using an external database or secret manager you don't need to run `--migrate` flag.
You must create the `secrets.yaml` and `values.yaml` and then run `abctl local install --values ./values.yaml --secret ./secrets.yaml`.
Please check [instructions](../../deploying-airbyte/integrations/database.md) to setup the external database as example.

:::

If you have data that you would like to migrate from an existing docker compose instance follow the steps below:

1. Make sure that you have stopped the instance running in docker compose, this may require the following command:

```
docker compose stop
```

2. Make sure that you have the latest version of abctl by running the following command:

```
curl -LsfS https://get.airbyte.com | bash -
```

3. Run abctl with the migrate flag set with the following command:

```
abctl local install --migrate
```

:::note

If you're using a version of Airbyte that you've installed with `abctl`, you can find instructions on upgrading your Airbyte installation [here](../../operator-guides/upgrading-airbyte.md#upgrading-with-abctl).

:::

-->






<!-- [[[move to deployment section for now]]]

## Customizing your Installation with a Values file

Optionally, you can use a `values.yaml` file to customize your installation of Airbyte. Create the `values.yaml` on your local storage. Then, apply the values you've defined by running the following command and adjusting the path to the `values.yaml` file as needed:

```shell
abctl local install --values ./values.yaml
```

Here's a list of common customizations.

- [External Database](../../deploying-airbyte/integrations/database)
- [State and Logging Storage](../../deploying-airbyte/integrations/storage)
- [Secret Management](../../deploying-airbyte/integrations/secrets)


## Using an EC2 Instance with abctl

This guide will assume that you are using the Amazon Linux distribution. However. any distribution that supports a docker engine should work with `abctl`. The launching and connecting to your EC2 Instance is outside the scope of this guide. You can find more information on how to launch and connect to EC2 Instances in the [Get started with Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html) documentation from Amazon.

1. Install the docker engine:

```shell
sudo yum install -y docker
```

2. Add the ec2-user (or whatever your distros default user) to the docker group:

```shell
sudo usermod -a -G docker ec2-user
```

3. Start and optionally enable (start on boot) the docker engine:

```shell
sudo systemctl start docker
sudo systemctl enable docker
```

4. Exit the shell and reconnect to the ec2 instance, an example would look like:

```shell
exit
ssh -i ec2-user-key.pem ec2-user@1.2.3.4
```

5. Download the latest version of abctl and install it in your path:

```shell
curl -LsfS https://get.airbyte.com | bash -
```

6. Run the `abctl` command and install Airbyte:
   :::tip
   By default, `abctl` only configures an ingress rule for the host `localhost`. In order to ensure that Airbyte can be accessed outside of the EC2 instance, you will need to specify the `--host` flag to the `local install` command, providing the FQDN of the host which is hosting Airbyte. For example, `abctl local install --host airbyte.company.example`.
   :::

By default, `abctl` will listen on port 8000. If port 8000 is already in used or you require a different port, you can specify this by passing the `--port` flag to the `local install` command. For example, `abctl local install --port 6598`

Ensure the security group configured for the EC2 Instance allows traffic in on the port (8000 by default, or whatever port was passed to `--port`) that you deploy Airbyte on. See the [Control traffic to your AWS resources using security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html) documentation for more information.

```shell
abctl local install --host [HOSTNAME]
```

### Running over HTTP

Airbyte suggest that you secure your instance of Airbyte using TLS. Running over plain HTTP allows attackers to see your
password over clear text. If you understand the risk and would still like to run Airbyte over HTTP, you must set
Secure Cookies to false. You can do this with `abctl` by passing the `--insecure-cookies` flag to `abctl`:

```shell
abctl local install --host [HOSTNAME] --insecure-cookies
```


-->
---
products: oss-community
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Quickstart

Airbyte Open Source is a reliable and extensible open source data pipeline.

If you're getting started with Airbyte Cloud, you can skip ahead to moving data by [adding your first source](add-a-source.md).

This quickstart guides you through creating a locally deployed instance of Airbyte in just minutes using `abctl` ([Airbyte Command Line Tool](https://github.com/airbytehq/abctl)). You'll be able to move data with minimal setup while you're exploring what Airbyte can do!

If you've already set up an Airbyte instance using Docker Compose and want to move to abctl, see the section on [migrating from Docker Compose](#migrating-from-docker-compose-optional).

:::tip
**When you're ready to put an Airbyte instance into production, you'll want to review our guides on deployment.**

For the best experience, we recommend [Deploying Airbyte on Kubernetes via Helm](../../deploying-airbyte/deploying-airbyte.md).

On a local deployment, Airbyte's default behavior is to store connector secrets in your configured database. These secrets are stored in plain text and are not encrypted. Refer to the [Secret Management documentation](../../deploying-airbyte/integrations/secrets.md) to set up an external secrets manager.
:::

If setting up an Airbyte server does not fit your use case needs (i.e. you're using Jupyter Notebooks or iterating on an early prototype for your project) you may find the [PyAirbyte](../pyairbyte/getting-started.mdx) documentation useful.

## Prerequisites

- To use `abctl`, you'll need to have **Docker Desktop** installed. See Docker's instructions for installation: [Mac](https://docs.docker.com/desktop/install/mac-install/), [Windows](https://docs.docker.com/desktop/install/windows-install/), [Linux](https://docs.docker.com/desktop/install/linux-install/)

## 1: Install `abctl`

The easiest method for installing `abctl` for Mac and Linux users is to use the following command:

```shell
curl -LsfS https://get.airbyte.com | bash -
```

If you would rather install `abctl` yourself, follow the instructions for your operating system:

<Tabs
defaultValue="abctl-mac">
<TabItem value="abctl-mac" label="Mac">

We recommend that Mac users use Brew to install the `abctl` command.

```bash
brew tap airbytehq/tap
brew install abctl
```

With Brew, you can keep abctl up to date easily, by running:

```bash
brew upgrade abctl
```

</TabItem>
<TabItem value="abctl-linux" label="Linux" default>

**1: Download the latest release of `abctl`.**

<a class="abctl-download button button--primary" data-architecture="linux-amd64" href="https://github.com/airbytehq/abctl/releases/latest" target="\_blank" style={{ marginRight: '10px' }} download>Latest linux-amd64 Release</a>
<a class="abctl-download button button--primary" data-architecture="linux-arm64" href="https://github.com/airbytehq/abctl/releases/latest" target="_blank" download>Latest linux-arm64 Release</a>
<br/>
<br/>

:::info

<details>
<summary>Be sure to download the file that is compatible with your machine's processor architecture.</summary>

You'll see two options: `linux-amd64` and `linux-arm64`
If you're unsure which one you need, running the following command will help:

```bash
uname -m
```

- If the output is `x86_64`, you have an x86-64 processor.
- If the output is `aarch64` or something similar, you have an ARM-based processor.
</details>

:::

**2: Extract the archive**

This will create a directory named abctl which contains the executable along with other needed files.

```bash
tar -xvzf {name-of-file-downloaded.linux-*.tar.gz}
```

**3: Make the extracted executable accessible**

This will allow you to run `abctl` as a command

```bash
chmod +x abctl/abctl
```

**4: Add `abctl` to your PATH**

This will allow you to run `abctl` from any directory in your terminal.

```bash
sudo mv abctl /usr/local/bin
```

**5: Verify the installation**

```bash
abctl version
```

If this command prints the installed version of the Airbyte Command Line Tool, it confirm that you are now ready to manage a local Airbyte instance using `abctl`.

</TabItem>
<TabItem value="abctl-windows" label="Windows" default>

**1: Download the latest release of `abctl`.**

<a class="abctl-download button button--primary" data-architecture="windows-amd64" href="https://github.com/airbytehq/abctl/releases/latest" target="_blank" download>Latest windows-amd64 Release</a>
<br/>
<br/>

**2: Extract the archive**

- Right click the zip file you've downloaded and select `Extract All...`, then choose a destination folder.

This creates a folder called abctl containing the abctl executable and other reqired files.

**3: Add the executable to your PATH**

- In the "System Properties" window (you can find this by searching for "enviornment variables" in the Start menu), click the `Environment Variables` button
- Under System variables, find the path and click to `Edit`
- Click `New` and add the path to the folder you extracted the abctl files to in the previous step.
- Click `OK` to save these changes.

**4: Open a new Command Prompt or PowerShell window**

This is important because changes to your PATH will only take effect in a newly opened window.

**5: Verify the installation**

```bash
abctl version
```

If this command prints the installed version of the Airbyte Command Line Tool, it confirm that you are now ready to manage a local Airbyte instance using `abctl`.

</TabItem>

</Tabs>

:::tip
For troubleshooting assistance, visit our [deployment troubleshooting guide](../../deploying-airbyte/troubleshoot-deploy).
:::

## 2: Run Airbyte

Ensure that Docker Desktop is up and running. Then, with abctl installed, the following command gets Airbyte running:

:::tip
By default, `abctl` only configures an ingress rule for the host `localhost`. If you plan to access Airbyte outside of `localhost`, you will need to specify the `--host` flag to the `local install` command, providing the FQDN of the host which is hosting Airbyte. For example, `abctl local install --host airbyte.company.example`.

By specifying the `--host` flag, Airbyte will be accessible to both `localhost` and the FDQN passed to the `--host` flag.
:::

```
abctl local install
```

Your browser may open automatically to the Airbyte Application. If not, access it by visiting [http://localhost:8000](http://localhost:8000).

You will be asked to enter your email address and an organization name. Your email address will be used to authenticate
to your instance of Airbyte. You will also need a password, which is randomly generated as part of the install command.
To get your password run:

```shell
abctl local credentials
```

Which should output something similar to:

```shell
Credentials:
  Email: user@company.example
  Password: random_password
  Client-Id: 03ef466c-5558-4ca5-856b-4960ba7c161b
  Client-Secret: m2UjnDO4iyBQ3IsRiy5GG3LaZWP6xs9I
```

Use the value in the password field to authenticate to your new Airbyte instance.

You can set your email and password with the `credentials` command using `abctl`. To set your email you can run:

```shell
abctl local credentials --email user@company.example
```

To set your password you can run:

```shell
abctl local credentials --password new_password
```

If you wish to configure authentication when install abctl, follow the documentation on the [Authentication Integration](../../deploying-airbyte/integrations/authentication)
page.

As long as your Docker Desktop daemon is running in the background, you can use Airbyte by returning to [http://localhost:8000](http://localhost:8000).

If you quit Docker Desktop and want to return to your local Airbyte workspace, just start Docker Desktop again. Once Docker finishes restarting, you'll be able to access Airbyte's local installation as normal.

### Suggested Resources

For the best performance, we suggest you run on a machine with 4 or more CPU's and at least 8 GB of memory. Currently
`abctl` does support running on 2 cpus and 8 gb of ram with the `--low-resource-mode` flag. You can pass the low
resource mode flag when install Airbyte with `abctl`:

```shell
abctl local install --low-resource-mode
```

Follow this [Github discussion](https://github.com/airbytehq/airbyte/discussions/44391) to upvote and track progress towards supporting lower resource environments.

## 3: Move Data

In the Building Connections section, you'll learn how to start moving data. Generally, there are three steps:

1: [Set up a Source](./add-a-source)

2: [Set up a Destination](./add-a-destination.md)

3: [Set up a Connection](./set-up-a-connection.md)

## Customizing your Installation with a Values file

Optionally, you can use a `values.yaml` file to customize your installation of Airbyte. Create the `values.yaml` on your local storage. Then, apply the values you've defined by running the following command and adjusting the path to the `values.yaml` file as needed:

```shell
abctl local install --values ./values.yaml
```

Here's a list of common customizations.

- [External Database](../../deploying-airbyte/integrations/database)
- [State and Logging Storage](../../deploying-airbyte/integrations/storage)
- [Secret Management](../../deploying-airbyte/integrations/secrets)

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

## Uninstalling

If you want to remove Airbyte from your system, consider which of the following two options you would like to use.

1: Run the following command to stop all running containers that `abctl` has created **while preserving any data you've created**:

```shell
abctl local uninstall
```

2: If you want to clear the persistent data in addition to stopping containers, run:

```shell
abctl local uninstall --persisted
```

As a last step, to clear out any additional information that `abctl` may have created, you can run:

```shell
rm -rf ~/.airbyte/abctl
```

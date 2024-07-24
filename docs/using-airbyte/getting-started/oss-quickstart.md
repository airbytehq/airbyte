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
:::

If setting up an Airbyte server does not fit your use case needs (i.e. you're using Jupyter Notebooks or iterating on an early prototype for your project) you may find the [PyAirbyte](../pyairbyte/getting-started.mdx) documentation useful.

## Prerequisites

- To use `abctl`, you'll need to have **Docker Desktop** installed. See Docker's instructions for installation: [Mac](https://docs.docker.com/desktop/install/mac-install/), [Windows](https://docs.docker.com/desktop/install/windows-install/), [Linux](https://docs.docker.com/desktop/install/linux-install/) 

## 1: Install `abctl`

Follow the instructions for your operating system:

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

<a class="abctl-download button button--primary" data-architecture="linux-amd64" href="https://github.com/airbytehq/abctl/releases/latest" target="_blank" style={{ marginRight: '10px' }} download>Latest linux-amd64 Release</a>
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
abctl --version
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

## 2: Run Airbyte

Ensure that Docker Desktop is up and running. Then, with abctl installed, the following command gets Airbyte running:

```
abctl local install
```

Your browser may open automatically to the Airbyte Application. If not, access it by visiting [http://localhost:8000](http://localhost:8000).

When prompted for a username and password, enter the following default values: 
- username: `airbyte`
- password: `password`

To set your own username and password, use command line flags or variables. For example, to set the username and password to foo and bar respectively, you can run the following command:

```bash
abctl local install --username foo --password bar
```

Or, if setting these values from environment variables, you'd export the following: 

```
export ABCTL_LOCAL_INSTALL_PASSWORD=foo
export ABCTL_LOCAL_INSTALL_USERNAME=bar
```

After supplying a username and password, you'll see the Airbyte workspace. Using this interface, you can set up and manage all your connections and move data with ease! 

As long as your Docker Desktop daemon is running in the background, you can use Airbyte by returning to [http://localhost8000](http://localhost8000). 

If you quit Docker Desktop and want to return to your local Airbyte workspace, just start Docker Desktop again. Once Docker finishes restarting, you'll be able to access Airbyte's local installation as normal. 

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

:::tip
`abctl` runs by default on port 8000. You can change the port by passing the `--port` flag to the `local install` command. Make sure that the security group that you have configured for the EC2 Instance allows traffic in on the port that you deploy Airbyte on. See the [Control traffic to your AWS resources using security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html) documentation for more information.
:::


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

```shell
abctl local install
```

### Editing the Ingress

By default `abctl` will install and Nginx Ingress and set the host name to `localhost`. You will need to edit this to
match the host name that you have deployed Airbyte to. To do this you will need to have the `kubectl` command installed
on your EC2 Instance and available on your path.

If you do not already have the CLI tool kubectl installed, please [follow these instructions to install](https://kubernetes.io/docs/tasks/tools/).

Then you can run `kubectl edit ingress -n airbyte-abctl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig` and edit the `host`
key under the spec.rules section of the Ingress definition. The host should match the FQDN name that you are trying to
host Airbyte at, for example: `airbyte.company.example`.

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

## Troubleshooting

There are several channels for community support of local setup and deployment. 

**GitHub Airbyte Forum's Getting Started FAQ:**<br/>Search the questions others have asked or ask a new question of your own in the [GitHub forum](https://github.com/airbytehq/airbyte/discussions/categories/questions).

**Airbyte Knowledge Base:**<br/>While support services are limited to Cloud and Enterprise customers, anyone may search the support team's [Help Center](https://support.airbyte.com/hc).

**Community Slack:**<br/>Helpful channels for troubleshooting include:<br/>
- [#ask-community-for-troubleshooting](https://airbytehq.slack.com/archives/C021JANJ6TY): Where members of the Airbyte community can ask and answer questions. 
- [#ask-ai](https://airbytehq.slack.com/archives/C01AHCD885S): For quick answers sourced from documentation and open support channels, you can have a chat with our virtual Airbyte assistant.  

**Introductory Course:**<br/>
On Udemy, [The Complete Hands-on Introduction to Airbyte](https://www.udemy.com/course/the-complete-hands-on-introduction-to-airbyte/) is a convenient and hands-on introduction to Airbyte that includes setting up example source and destination configurations. You'll also go on to use it in conjunction with Apache Airflow, Snowflake, dbt, and more.

**Bug Reports:**<br/>If you find an issue with the `abctl` command, please report it as a github
issue [here](https://github.com/airbytehq/airbyte/issues) with the type of `🐛 [abctl] Report an issue with the abctl tool`.

**Releases:**<br/>If you'd like to select which release of abctl to run, you can find the list of releases [here](https://github.com/airbytehq/abctl/releases/).
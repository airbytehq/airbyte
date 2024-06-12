---
products: oss-community
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";



# OSS Quickstart

Airbyte Open Source is a reliable and extensible open source data pipeline.

This quickstart will help you to get started with a locally deployed instance of Airbyte in just minutes using abctl (Airbyte Command Line Tool). 

:::tip
You can learn more about abctl on the associated [GitHub repository](https://github.com/airbytehq/abctl). 
:::

## Prerequisites

- To use abctl, you'll need to have **Docker Desktop** installed. See Docker's instructions for installation: [Mac](https://docs.docker.com/desktop/install/mac-install/), [Windows](https://docs.docker.com/desktop/install/windows-install/), [Linux](https://docs.docker.com/desktop/install/linux-install/)

## Install abctl

Follow the instructions for your operating system:

<Tabs
defaultValue="abctl-mac">
<TabItem value="abctl-mac" label="Mac">

We recommend that Mac users use Brew to install the `abctl` command. 

```
brew tap airbytehq/tap
brew install abctl
```

With Brew, you can keep abctl up to date easily, by running:
```
brew upgrade abctl
``` 

:::info
If you don't want to use Brew to manage the installation, you can manually download the latest release [here](https://github.com/airbytehq/abctl/releases).
:::

</TabItem>
<TabItem value="abctl-linux" label="Linux" default>

**1: Download the latest release of `abctl` [here](https://github.com/airbytehq/abctl/releases)**

:::info
Be sure to download the file that is compatible with your machine's processor architecture. 
:::

You'll see two options: `linux-amd64` and `linux-arm64`
If you're unsure which one you need, running the following command will help:

```
uname -m
```

- If the output is `x86_64`, you have an x86-64 processor.
- If the output is `aarch64` or something similar, you have an ARM-based processor.

**2: Extract the archive**

This will create a directory named abctl which contains the executable along with other needed files. 

```
Bash

tar -xvzf {name-of-file-downloaded.linux-*.tar.gz}
```

**3: Make the extracted executable accessible**

This will allow you to run `abctl` as a command

```
Bash

chmod +x abctl/abctl
```

**4: Add `abctl` to your PATH**

This will allow you to run `abctl` from any directory in your terminal. 

```
Bash

sudo mv abctl /usr/local/bin
```
**5: Verify the installation**

```
Bash

abctl --version
```

If this command prints the installed version of the Airbyte Command Line Tool, it confirm that you are now ready to manage a local Airbyte instance using `abctl`.


</TabItem>
<TabItem value="abctl-windows" label="Windows" default>

**1: Download the latest release of `abctl` [here](https://github.com/airbytehq/abctl/releases)**

**2: Extract the archive**
- Right click the zip file you've downloaded and select "Extract All...", then choose a destination folder. 

This creates a folder called abctl containing the abctl executable and other reqired files. 

**3: Add the executable to your PATH**
- In the "System Properties" window (you can find this by searching for "enviornment variables" in the Start menu), click the `Environment Variables` button
- Under System variables, find the path and click to `Edit`
- Click `New` and add the path to the folder you extracted the abctl files to in the previous step. 
- Click `OK` to save these changes. 

**4: Open a new Command Prompt or PowerShell window**

This is important because changes to your PATH will only take effect in a newly opened window. 

**5. Verify the installation**

```
Bash

abctl --version
```

If this command prints the installed version of the Airbyte Command Line Tool, it confirm that you are now ready to manage a local Airbyte instance using `abctl`.


</TabItem>

</Tabs>

## Run Airbyte

Ensure that Docker Desktop is up and running. Then, once  abctl is installed, you can run Airbyte with the following command:

```
abctl local install
```

Your browser may open automatically to the Airbyte Application. If not, access it by visiting [http://localhost8000](http://localhost8000).

When prompted for a username and password, you can enter the following default values: 
- username: `airbyte`
- password: `password`

To set your own username and password, use command line flags or variables. For example, to set the username and password to foo and bar respectively, you can run the following command:

```
abctl local install --username foo --password bar
```

Or, if setting these values in the .env file, you'd add the following: 

```
ABCTL_LOCAL_INSTALL_PASSWORD=foo
ABCTL_LOCAL_INSTALL_USERNAME=bar
```

After supplying username and password you'll see the Airbyte workspace. Using  this interface, you can set up and manage all your connections and move data with ease! 

As long as your Docker Desktop daemon is running in the background, you can use Airbyte by returning to [http://localhost8000](http://localhost8000). 

If you quit Docker Decktop and want to return to your local Airbyte workspace, just start Docker Desktop again. After a short period of time, you'll be able to access Airbyte's local installation normally. 

## Troubleshooting Support

There are several channels for community support of local setup and deployment. 

**GitHub Airbyte Forum's Getting Started FAQ:**
 - Search the questions others have asked or ask a new question of your own. 

**Airbyte Knowledge Base:**
- While support services are limited to Cloud and Enterprise customers, anyone may search the support team's [Help Center](https://support.airbyte.com/hc).

**Community Slack** 
Helpful channels for troubleshooting include:
- [#ask-community-for-troubleshooting](https://airbytehq.slack.com/archives/C021JANJ6TY)
- [#ask-ai](https://airbytehq.slack.com/archives/C01AHCD885S)


## Next Steps

In the Building Connections section, you'll learn how to start moving data. Generally, there are three steps: 

1: [Set up a Source](./add-a-source)

2: [Set up a Destination](./add-a-destination.md)

3: [Set up a Connection](./set-up-a-connection.md)

**Introductory Course**

For an in-depth introduction to Airbyte that includes setting up example source and destination configurations, we recommend the Udemy course [The Complete Hands-in Introduction to Airbyte](https://www.udemy.com/course/the-complete-hands-on-introduction-to-airbyte/).
---
products: oss-community
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWindows } from "@fortawesome/free-brands-svg-icons";

# Quickstart

This quickstart guides you through deploying a local instance of Airbyte Self-Managed Community, Airbyte's open source product. Setup only takes a few minutes, and you can start moving data immediately.

## Overview

This quickstart shows you how to:

- [Install abctl](#part-1-install-abctl)
- [Run Airbyte](#part-2-run-airbyte)
- [Set up authentication](#part-3-set-up-authentication)
- [Decide on your next steps](#whats-next)

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

### Install abctl the fast way (Mac, Linux)

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

    1. Press <kbd><FontAwesomeIcon icon={faWindows} /> Windows</kbd> + <kbd>I</kbd>.

    2. Click **System** > **About**.

    3. Next to **Processor**, if it says `AMD`, you'll download the **windows-amd64** release. If the output is `ARM` or similar, you'll download the **windows-arm64** release.

2. Download the latest release of `abctl`.

    <a class="abctl-download button button--primary" data-architecture="windows" href="https://github.com/airbytehq/abctl/releases/latest" target="_blank" download>Latest Windows Release</a>

3. Extract the zip file to a destination of your choice. This creates a folder containing the abctl executable and other required files. Copy the filepath because you'll need this in a moment.

4. Add the executable to your `Path` environment variable.

    1. Click <FontAwesomeIcon icon={faWindows} /> **Start** and type `environment`.

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

    :::note
    If you see the warning `Encountered an issue deploying Airbyte` with the message `Readiness probe failed: HTTP probe failed with statuscode: 503`, allow installation to continue. You may need to allocate more resources for Airbyte, but installation will complete anyway. See [Suggested resources](#suggested-resources).
    :::

    Installation may take up to 15 minutes depending on your internet connection. When it completes, your Airbyte instance opens in your web browser at [http://localhost:8000](http://localhost:8000). As long as your Docker Desktop daemon is running in the background, use Airbyte by returning to [http://localhost:8000](http://localhost:8000). If you quit Docker Desktop and want to return to Airbyte, start Docker Desktop again. Once your containers are running, you can access Airbyte normally.

3. Enter your **Email** and **Organization name**, then click **Get Started**. Airbyte asks you to log in with a password.

## Part 3: Set up authentication

To access your Airbyte instance, you need a password.

1. Get your default password.

    ```bash
    abctl local credentials
    ```

    This outputs something like this:

    ```shell
    Credentials:
    Email: user@example.com
    // highlight-next-line
    Password: random_password
    Client-Id: 03ef466c-5558-4ca5-856b-4960ba7c161b
    Client-Secret: m2UjnDO4iyBQ3IsRiy5GG3LaZWP6xs9I
    ```

2. Return to your browser and use that password to log into Airbyte.

3. Optional: Since you probably want to set your own password, you can change it any time.

    ```bash
    abctl local credentials --password YourStrongPasswordExample
    ```

    Your Airbyte server restarts. Once it finishes, use your new password to log into Airbyte again.

## What's next

Congratulations! You have a fully functional instance of Airbyte running locally.

### Move data

In Airbyte, you move data from [sources](./add-a-source) to [destinations](./add-a-destination.md). The relationship between a source and a destination is called a [connection](./set-up-a-connection.md). Try moving some data on your local instance.

### Deploy Airbyte

If you want to scale data movement in your organization, you probably need to move Airbyte off your local machine. You can deploy to a cloud provider like AWS, Google Cloud, or Azure. You can also use a single node like an AWS EC2 virtual machine. See the [deployment guide](../../deploying-airbyte/) to learn more.

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

<!-- --Preserving for posterity but probably not relevant to include in the quick start. May move to deployment section later.--

## Customizing your Installation with a Values file

Optionally, you can use a `values.yaml` file to customize your installation of Airbyte. Create the `values.yaml` on your local storage. Then, apply the values you've defined by running the following command and adjusting the path to the `values.yaml` file as needed:

```shell
abctl local install --values ./values.yaml
```

Here's a list of common customizations.

- [External Database](../../deploying-airbyte/integrations/database)
- [State and Logging Storage](../../deploying-airbyte/integrations/storage)
- [Secret Management](../../deploying-airbyte/integrations/secrets)
-->

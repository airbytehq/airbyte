---
products: enterprise-flex
sidebar_label: Deploy a data plane with Airbox
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Deploy a data plane with Airbox in Enterprise Flex

Airbox is Airbyte's command line tool for managing Airbyte data planes on Kubernetes. It's the ideal way to deploy and manage data planes for teams that have limited Kubernetes expertise and don't want to deploy with Helm.

The installation process consists of these steps:

1. Install Airbox

2. Configure Airbox

3. Authenticate with Airbyte

4. Install your data plane

5. Verify your data plane is working correctly

## Prerequisites

### Airbyte subscription requirements

- An active subscription to Airbyte Enterprise Flex
- You must be an Instance Admin to manage data planes

### Infrastructure requirements

- Kubernetes cluster? No, single node like EC2 or local machine
- Helm?
- Kind? 
- Docker - same setup as abctl

### Security considerations

### Workspaces

Have a workspace to use. Create it if needed.

## 1. Install Airbox

<!-- We'll probably distribute this with brew or something like abctl. For now, you have to build it manually. It's something like this. If you have $PATH problems, just run it as ./airbox instead of airbox -->

1. Install the [latest version of Go](https://go.dev/dl/).

2. Build Airbox from the source code.

    1. Clone the [abctl](https://github.com/airbytehq/abctl/tree/bernielomax/feat/dataplane-management) repo locally.

    2. From that directory, build Airbox.

        ```bash
        go build -o airbox ./cmd/airbox
        ```

3. Add Airbox to your $PATH.

    1. First, check if `~/go/bin/` is in tour $PATH.

        ```bash
        echo $PATH | tr ':' '\n'
        ```

    2. If it's not, add it.

        ```bash
        $ export PATH="$PATH:$(go env GOPATH)/bin"
        $ source ~/.bashrc
        $ which airbox

        # Expected output is similar to this
        /home/youruser/go/bin/airbox
        ```

    Add Airbox to your $PATH...

## 2. Set credentials {#set-credentials}

You need an Airbyte application so Airbox can access your control plane. [Create one](#) and note the Client ID and Client Secret. If you already have an application, you can skip creating one and reuse existing credentials.

1. In Airbyte's UI, click your user name > **User Settings** > **Applications** >> **Create an application**.

2. Enter a descriptive application name. For example, "Data plane deployment." Airbyte creates your application. Note the Client ID and Client Secret.

3. In your terminal, set the application credentials you created as environment variables.

    ```bash
    export AIRBYTE_CLIENT_ID="<CLIENT_ID>"
    export AIRBYTE_CLIENT_SECRET="<CLIENT_SECRET>"
    ```

## 3. Configure Airbox

After you enter your client ID and client secret, configure Airbyte to access your Cloud control plane.

1. Configure Airbox to interact with your Airbyte control plane.

    ```bash
    airbox config init
    ```

2. Select **Cloud** when Airbox asks you to select your Airbyte deployment type.

<!-- This ended abruptly for me - check that this is all that's necessary. -->

## 4. Authenticate with Airbyte

After configuring Airbyte, but before you can manage data planes, you must authenticate with it. You can also log out and, if you work in multiple organizations, switch between them.

### Log in

After you configure Airbyte, authenticate with it. Run the following command.

```bash
airbox auth login
```

You should see this result.

```bash
Authenticating with Airbyte

Connecting to: https://api.airbyte.com

Successfully authenticated!
```

### Log out

If you need to log out and clear your stored credentials, run this command.

```bash
airbox auth logout
```

To manage data planes again, return to [step 2](#set-credentials).

### Switch organizations

If you use multiple Airbyte organizations, you can switch between them with the following command.

```bash
airbox auth switch-organization
```

Choose the new organizaton you want to connect to and press <kbd>Enter</kbd>.

## 5. Deploy a data plane

After you authenticate with Airbyte, you can deploy a data plane.

1. Install your data plane.

    ```bash
    airbox install dataplane
    ```

2. Follow the prompts in the terminal.

    1. Choose whether you want to create a new region or use an existing one.
    
        :::tip
        To avoid confusion later, your regions in Airbyte should reflect the actual regions your data planes run in. For example, if you are installing this data plane in the AWS `us-west-1` region, you may wish to call it `us-west-1` or something similar.
        :::

    2. Name your data plane.

    The process looks similar to this.

    ```bash
    $ airbox install dataplane

    Starting interactive dataplane installation

    Select region option:

    Use existing region
    > Create new region

    Enter new region name:
    > us-west-1

    Enter dataplane name:
    > us-west-1-dataplane-1

    Dataplane Credentials:
    DataplaneID: <dataplane_ID>
    ClientID: <client_ID>
    ClientSecret: <client_secret>

    Dataplane 'us-west-1' installed successfully!
    ```

## 6. Assign a workspace to your data plane

In Airbyte's UI, follow these steps.

1. Click **Workspace settings** > **General**.

2. Under **Region**, select the data plane you created.

## 7. Verify your data plane is running correctly

Once you assign your workspace to your data plane, verify that data plane runs syncs and creates pods correctly.

1. Add the [Sample Data](#) source, which generates non-sensitive sample data.

2. Add the [End-to-End Testing (/dev/null)](#) destination. If you want to actually see the data in the destination, [Google Sheets](#) is a good option too because it's easy to set up.

3. Create a connection between them.

4. In your terminal, run `kubectl get po -w`.

5. Start a sync.

6. Watch the pods start and complete. You should see something similar to this.

    ```bash
    NAME                                            READY   STATUS            RESTARTS   AGE
    us-west-1-airbyte-data-plane-c8858dd77-t55wn    1/1     Running           0          41m
    replication-job-49346750-attempt-0              0/3     Completed         0          20m
    source-faker-discover-49350414-0-cxrhx          0/2     Pending           0          0s
    source-faker-discover-49350414-0-cxrhx          0/2     Pending           0          1s
    source-faker-discover-49350414-0-cxrhx          0/2     Init:0/1          0          1s
    source-faker-discover-49350414-0-cxrhx          0/2     Init:0/1          0          2s
    source-faker-discover-49350414-0-cxrhx          0/2     PodInitializing   0          9s
    source-faker-discover-49350414-0-cxrhx          2/2     Running           0          10s
    source-faker-discover-49350414-0-cxrhx          1/2     NotReady          0          13s
    source-faker-discover-49350414-0-cxrhx          0/2     Completed         0          19s
    replication-job-49350414-attempt-0              0/3     Pending           0          0s
    replication-job-49350414-attempt-0              0/3     Pending           0          0s
    replication-job-49350414-attempt-0              0/3     Init:0/1          0          0s
    replication-job-49350414-attempt-0              0/3     Init:0/1          0          1s
    source-faker-discover-49350414-0-cxrhx          0/2     Completed         0          20s
    replication-job-49350414-attempt-0              0/3     PodInitializing   0          17s
    replication-job-49350414-attempt-0              3/3     Running           0          18s
    replication-job-49350414-attempt-0              2/3     NotReady          0          31s
    replication-job-49346750-attempt-0              0/3     Completed         0          29m
    replication-job-49346750-attempt-0              0/3     Completed         0          29m
    source-faker-discover-49350414-0-cxrhx          0/2     Completed         0          12m
    source-faker-discover-49350414-0-cxrhx          0/2     Completed         0          12m
    ```

## Manage existing data planes

#### List all data planes

#### Delete a data plane

### Where Airbyte stores configuration files

Airbox stores configuration data in `~/.airbyte/airbox/config.yaml`. This includes:

- Authentication credentials
- Context settings
- Organization and workspace IDs

---
products: enterprise-flex
sidebar_label: Deploy a data plane with Airbox
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Deploy a data plane with Airbox in Enterprise Flex

Airbox is Airbyte's command line tool for managing Airbyte data planes on Kubernetes. It's the ideal way to deploy and manage data planes for teams that have limited Kubernetes expertise or don't want to deploy with Helm.

At the end of this guide, you'll have an Airbyte workspace that runs connections using a self-managed data plane.

## Prerequisites

Before you begin, ensure you satisfy all of these requirements.

### Subscription and permission requirements

- An active subscription to Airbyte Enterprise Flex
- You must be an organization Admin to manage data planes

### Infrastructure requirements

- A single-node on which to deploy your data plane. This can be a virtual machine from a Cloud provider, a bare metal server, or even your local computer.

    - Minimum specs: 8 CPUs and 16 GB of RAM
    - Recommended specs: 8 CPUs and 24 GB of RAM

### Software requirements

- Docker Desktop or Docker Engine (installation is described below)

- To manage and monitor your data plane after installation, you should also install these command line tools, although this isn't strictly necessary.

    - [Helm](https://helm.sh/)
    - [kind](https://kind.sigs.k8s.io/)
    - [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl)

### Security considerations

- Self-managed data planes require egress from your network to Airbyte's managed control plane.
- Self-managed data planes only send requests to the control plane. The control plane must be able to send responses to the data plane, but not requests.

### Workspaces

You should already have considered [what regions and workspaces](getting-started) you need to satisfy your compliance and data sovereignty needs.

## Part 1. Install Airbox

You can install the latest version of Airbox [as a binary](https://github.com/airbytehq/abctl/releases). Downloads are available for Windows, Mac, and Linux.

## Part 2: Install Docker Desktop

Install Docker Desktop on the machine that will host your data plane. Follow the steps for your operating system in Docker's online help, linked below.

- [Mac](https://docs.docker.com/desktop/install/mac-install/)
- [Windows](https://docs.docker.com/desktop/install/windows-install/)
- [Linux](https://docs.docker.com/desktop/install/linux-install/) - If you're installing on a Linux headless virtual machine, it's easier to use [Docker Engine](https://docs.docker.com/engine/install/) instead of Docker Desktop.

You don't need to do anything with Docker, but you do need to run it in the background. Once it's open, minimize it and proceed to Part 3.

:::info Why do you need Docker?
Airbyte runs on Kubernetes. When you deploy your data plane, Airbyte uses Docker to create a Kubernetes cluster on the computer hosting the data plane.
:::

## Part 3: Set credentials {#set-credentials}

You need an Airbyte application so Airbox can access your control plane. If you don't have one, create one and note the Client ID and Client Secret. If you already have one, you can skip creating one and reuse your existing credentials.

1. In Airbyte's UI, click your user name > **User settings** > **Applications** > **Create an application**.

2. Enter a descriptive application name. For example, "Data plane deployment." Airbyte creates your application. Note the Client ID and Client Secret.

3. In your terminal, set the application credentials you created as environment variables.

    ```bash
    export AIRBYTE_CLIENT_ID="<CLIENT_ID>"
    export AIRBYTE_CLIENT_SECRET="<CLIENT_SECRET>"
    ```

## Part 4: Configure Airbox

After you enter your client ID and client secret, configure Airbox to access your Cloud control plane.

1. Configure Airbox to interact with your Airbyte control plane.

    ```bash
    airbox config init
    ```

2. Select **Enterprise Flex** and press <kbd>Enter</kbd>

## Part 5: Authenticate with Airbyte

After configuring Airbyte, but before you can manage data planes, you must authenticate with it. You can also log out and, if you work in multiple organizations, switch between them.

### Log in

After you configure Airbyte, authenticate with it. Run the following command so Airbox can use the client ID and client secret you set earlier to authenticate with your Airbyte environment.

```bash
airbox auth login
```

You see the following result.

```bash
Authenticating with Airbyte

Connecting to: https://api.airbyte.com

Successfully authenticated!
```

Continue to Part 6.

### Log out

If you need to clear the authentication token Airbox uses to access your data plane, log out.

```bash
airbox auth logout
```

This doesn't remove the client ID and client secret from Airbyte. If you need to rotate credentials, you must also delete [your application](../using-airbyte/configuring-api-access).

### Switch organizations

1. If you use multiple Airbyte organizations, you can switch between them with the following command.

    ```bash
    airbox auth switch-organization
    ```

    If you belong to multiple organizations, Airbox shows you that list. If not, Airbox automatically sets you to your single organization again.

2. Choose the new organization you want to connect to and press <kbd>Enter</kbd>.

## Part 6: Deploy a data plane

After you authenticate with Airbyte, run the install command. This begins a process that creates a new kind cluster in Docker, registers the data plane with Airbyte's managed control plane, and deploys the data plane for use.

1. Install your data plane.

    ```bash
    airbox install dataplane
    ```

2. Follow the prompts in the terminal.

    1. Choose whether you want to create a new region or use an existing one (if you have some).

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

    Dataplane 'us-west-1-dataplane-1' installed successfully!
    ```

## Part 7: Assign a workspace to your data plane

If this data plane is in a new region, or you want a workspace to use this region now, in Airbyte's UI, follow these steps.

1. Click **Workspace settings** > **General**.

2. Under **Region**, select the region you created that contains your data plane.

## Part 8: Verify your data plane is running correctly

Once you assign your workspace to your data plane, verify that data plane runs syncs and creates pods correctly.

1. Create a connection.

    1. Add the [Sample Data](/integrations/sources/faker) source, which generates non-sensitive sample data.

    2. Add the [End-to-End Testing (/dev/null)](/integrations/destinations/dev-null) destination if you don't need to see the data. If you want to see the data in the destination, [Google Sheets](/integrations/destinations/google-sheets) is also a good option that's easy to set up.

    3. [Create a connection](../move-data/add-connection) between that source and destination.

2. In your terminal, run `watch kubectl get po` or `kubectl get po -w`. This allows you to watch pods progress in your Kubernetes cluster.

3. In Airbyte's UI, start the sync.

4. Watch pods start, make progress, and complete. You should see something similar to this.

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

5. In Airbyte's UI, ensure the sync completes and populates the expected number of records, based on your settings for the Sample Data source.

<!-- ## Manage existing data planes

Once a data plane is running, you can manage and delete it if necessary.

### List all data planes

```bash
airbox get dataplane
```

### Delete a data plane

The following command removes the data plane registration from Airbyte.

```bash
airbox delete dataplane <dataplane_id>
```

However, the data plane continues to exist. To complete deletion, use Helm to uninstall the release from Kubernetes.

1. Find your data plane's release and namespace.

    ```bash
    helm list -A
    ```

    This returns something similar to this.

    ```bash
    NAME      	            NAMESPACE	REVISION	UPDATED                             	STATUS  	CHART                   	APP VERSION
    us-west-1-data-plane	default  	1       	2025-09-09 16:36:12.282242 -0700 PDT	deployed	airbyte-data-plane-1.8.1	1.8.1      
    ```

2. Uninstall the release. From the preceding result, use `NAME` as the `release-name` and `NAMESPACE` as the `namespace`.

    ```bash
    helm uninstall <release-name> -n <namespace>
    ```

3. If this data plane belonged to a region you no longer need, you can also delete the region with Airbyte's API.

    ```curl
    curl -X DELETE https://api.airbyte.com/v1/regions/{regionId} \
    --header "Authorization: Bearer $TOKEN" 
    ```-->

## Where Airbox stores configuration files

Airbox stores configuration data in `~/.airbyte/airbox/config.yaml`. This includes:

- Authentication credentials
- Context settings
- Organization and workspace IDs

## Restart a data plane

As long as Docker Desktop is running in the background, your data plane remains available. If you quit Docker Desktop or restart your virtual machine and want to restore your data plane, start Docker Desktop again. Once your containers are running, your data plane can resume work.

## Values.yaml not currently supported

Airbox doesn't currently support deployment customization with values.yaml files.

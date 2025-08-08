---
products: oss-community
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWindows } from "@fortawesome/free-brands-svg-icons";
import EnvironmentVarConversion from '@site/static/_extraenv_to_helm_chart_v2.md';
import HelmSyntaxConversion from '@site/static/_helm-chart-2-syntax-changes.md';


# abctl

abctl is Airbyte's open source command line tool to create and manage local instances of Airbyte running in Docker.

## Overview of abctl

Airbyte runs on Kubernetes. People run Airbyte in a diverse set of environments like a local computer, a bare metal server, or a virtual machine. However, you might not be running Kubernetes and might not even know much about it. abctl makes it easy to run Airbyte anywhere Docker is running.

### When to use abctl

You use abctl to run Airbyte on a machine that isn't running a Kubernetes cluster, but is running Docker. Normally, you don't use abctl to manage enterprise deployments, because they use dedicated Kubernetes infrastructure. However, it's possible to use abctl this way if you want to.

### What abctl does

abctl uses [kind](https://kind.sigs.k8s.io/) to create a [Kubernetes](https://kubernetes.io/) cluster inside a [Docker](https://www.docker.com/) container. Then, it uses [Helm](https://helm.sh/) to install the latest Airbyte and [NGINX Ingress Controller](https://docs.nginx.com/nginx-ingress-controller/) Helm charts. It also helps you manage and understand that infrastructure.

![](abctl-diagram.png)

## Before you start

Before you use abctl, install Docker Desktop on your machine: 

- [Mac](https://docs.docker.com/desktop/install/mac-install/).
- [Windows](https://docs.docker.com/desktop/install/windows-install/).
- [Linux](https://docs.docker.com/desktop/install/linux-install/). If you're installing on a Linux headless virtual machine, you may have an easier time using [Docker Engine](https://docs.docker.com/engine/install/) instead of Docker Desktop. See [the EC2 guide](../abctl-ec2) for an example.

## Install abctl

To install abctl, follow the instructions for your operating system.

<Tabs defaultValue="abctl-curl">

<TabItem value="abctl-curl" label="curl">

Use curl to install abctl.

1. Open a terminal and run the following command.

    ```shell
    curl -LsfS https://get.airbyte.com | bash -
    ```

2. If your terminal asks you to enter your password, do so.

When installation completes, you see `abctl install succeeded`.

</TabItem>
<TabItem value="abctl-go" label="Go">

Use [go install](https://go.dev/ref/mod#go-install) to install abctl.

Open a terminal and run the following command.

```bash
go install github.com/airbytehq/abctl@latest
```

</TabItem>
<TabItem value="abctl-brew" label="Homebrew">

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
<TabItem value="abctl-linux" label="GitHub - Linux">

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
<TabItem value="abctl-windows" label="GitHub - Windows">

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

## Install and manage local Airbyte instances

This section shows you how to use abctl. It's not a step-by-step guide to deploy Airbyte. See Airbyte's [Quickstart](../../using-airbyte/getting-started/oss-quickstart.md) or [deployment guides](../deploying-airbyte.md) for a complete explanation.

### Install or update Airbyte

To install or update Airbyte, run:

```bash
abctl local install
```

Optional flags are available and you can combine them in powerful ways. For example, you can create a Kubernetes secret and customize your Airbyte installation using a yaml file to make use of that secret.

```bash
abctl local install --secret YOUR_SECRET --values values.yaml
```

For a list of all flags, see the [full reference](#reference).

:::note
Depending on your internet speed, `abctl local install` may take up to 30 minutes.
:::

### Get information about your Airbyte instance

If an Airbyte installation exists, you can get critical information about that installation.

```bash
abctl local status
```

For example:

```bash
$ abctl local status
Existing cluster 'airbyte-abctl' found
Found helm chart 'airbyte-abctl'
  Status: deployed
  Chart Version: 0.422.2
  App Version: 0.63.15
Found helm chart 'ingress-nginx'
  Status: deployed
  Chart Version: 4.11.1
  App Version: 1.11.1
Airbyte should be accessible via http://localhost:8000
```

### View and change credentials

If an Airbyte installation exists, you can view and update the credentials needed to access that installation.

To view credentials, run:

```bash
abctl local credentials
```

To update credentials, run:

```bash
abctl local credentials --email YOUR_EMAIL --password YOUR_PASSWORD
```

abctl returns something like this:

```bash
{
  "email": "[YOUR EMAIL]",
  "password": "[RANDOM PASSWORD]",
  "client-id": "[RANDOM CLIENT-ID]",
  "client-secret": "[RANDOM CLIENT-SECRET]"
}
```

### Manage your local Kubernetes instance

To display Kubernetes deployment information, run:

```bash
abctl local deployments
```

If you need to restart Kubernetes, run:

```bash
abctl local deployments --restart
```

### Uninstall Airbyte

To stop running all containers, but keep your data, run:

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

## Helm chart V2 (abctl versions 0.30 and later)

Airbyte has upgraded its Helm chart to a new version called "V2." abctl versions 0.30 and later use Helm chart V2 by default. abctl versions 0.29 and earlier only use Helm chart V1.

:::note
Many abctl users don't use external integrations. For example, you might run a local deployment on `localhost` without a `values.yaml` file. If this is the case for you, you can safely ignore this section. Continue upgrading Airbyte in the usual way.
:::

### Which chart you should use

You should use the latest version of the Helm chart. Doing so automatically installs the latest compatible version of Airbyte, unless you have a reason not to use it. 

Typically, the only reason not to use Helm chart V2 is that you have complex configurations in your `values.yaml` file and you aren't ready to upgrade them. Although using Helm chart V2 is currently optional, at a point in the future, it will be mandatory. Airbyte recommends switching as soon as you're able to.

Because Helm chart V2 is currently optional, the version of the Helm chart and the version of the Airbyte platform aren't necessarily the same. For example, your Helm chart version can be `2.03`, which is compatible with Airbyte's platform version `1.7.0`.

### How to control the Helm chart version

You can use the `--chart-version` and `--set` flags to override the Helm chart and Airbyte platform versions. Helm chart V2 is usable with Airbyte versions 1.6.0 and later. Earlier versions of Airbyte only support Helm chart V1.

- To install the latest version of the Helm chart with the latest version of the Airbyte platform:

    ```bash
    abctl local install
    ```

- To install a specific chart version:

    ```bash
    abctl local install --chart-version 2.0.3
    ```

- To install a specific platform version:

    ```bash
    abctl local install --set global.image.tag=1.7.0
    ```

### How to update your values.yaml file

In most cases, the adjustments to `values.yaml` are small and involve changing keys and moving sections. This section walks you through the main updates you need to make. If you already know what to do, see [Values.yaml reference](../deploying-airbyte/values) for the full V1 and V2 interfaces.

Airbyte recommends approaching this project in this way:

1. Note the customizations in your V1 `values.yaml` file to ensure you don't forget anything.

2. Start with a basic V2 `values.yaml` to verify that it works. Map your V1 settings to V2, transferring one set of configurations at a time.

3. Don't test in production.

Follow the steps below to start generating `values.yaml`.

<details>
<summary>
Create a `values.yaml` file and a `global` configuration
</summary>

Create a new `values.yaml` file on your machine. In that file, create your basic global configuration.

```yaml title="values.yaml"
global:
  edition: community

  airbyteUrl: "" # The URL where Airbyte will be reached; This should match your Ingress host
```

</details>

<details>
<summary>
Add your database (if applicable)
</summary>

Disable Airbyte's default Postgres database and add your own. The main difference in Helm chart V2 is the `global.database.database` key has changed to `global.database.name`.

```yaml title="values.yaml"
global: 
  database:
    # -- Secret name where database credentials are stored
    secretName: "" # e.g. "airbyte-config-secrets"
    # -- The database host
    host: ""
    # -- The database port
    port:
    # -- The database name - this key used to be "database" in Helm chart 1.0
    name: ""

    # Use EITHER user or userSecretKey, but not both
    # -- The database user
    user: ""
    # -- The key within `secretName` where the user is stored
    userSecretKey: "" # e.g. "database-user"

    # Use EITHER password or passwordSecretKey, but not both
    # -- The database password
    password: ""
    # -- The key within `secretName` where the password is stored
    passwordSecretKey: "" # e.g."database-password"

postgresql:
  enabled: false
```

</details>

<details>
<summary>
Add external logging (if applicable)
</summary>

```yaml
global:
  storage:
    secretName: ""
    type: minio # default storage is minio. Set to s3, gcs, or azure, according to what you use.

    bucket:
      log: airbyte-bucket
      auditLogging: airbyte-bucket # Version 1.7 or later, only if you're using audit logging
      state: airbyte-bucket
      workloadOutput: airbyte-bucket
      activityPayload: airbyte-bucket

    # Set ONE OF the following storage types, according to your specification above

    # S3
    s3:
      region: "" ## e.g. us-east-1
      authenticationType: credentials ## Use "credentials" or "instanceProfile"
      accessKeyId: ""
      secretAccessKey: ""

    # GCS
    gcs:
      projectId: <project-id>
      credentialsJson:  <base64-encoded>
      credentialsJsonPath: /secrets/gcs-log-creds/gcp.json

    # Azure
    azure:
      # one of the following: connectionString, connectionStringSecretKey
      connectionString: <azure storage connection string>
      connectionStringSecretKey: <secret coordinate containing an existing connection-string secret>
```

</details>

<details>
<summary>
Add external connector secret management (if applicable)
</summary>

```yaml
global:
  secretsManager:
    enabled: false
    type: "" # one of: VAULT, GOOGLE_SECRET_MANAGER, AWS_SECRET_MANAGER, AZURE_KEY_VAULT, TESTING_CONFIG_DB_TABLE
    secretName: "airbyte-config-secrets"

    # Set ONE OF the following groups of configurations, based on your configuration in global.secretsManager.type.

    awsSecretManager:
      region: <aws-region>
      authenticationType: credentials ## Use "credentials" or "instanceProfile"
      tags: ## Optional - You may add tags to new secrets created by Airbyte.
      - key: ## e.g. team
          value: ## e.g. deployments
        - key: business-unit
          value: engineering
      kms: ## Optional - ARN for KMS Decryption.

    # OR

    googleSecretManager:
      projectId: <project-id>
      credentialsSecretKey: gcp.json

    # OR

    azureKeyVault:
      tenantId: ""
      vaultUrl: ""
      clientId: ""
      clientIdSecretKey: ""
      clientSecret: ""
      clientSecretSecretKey: ""
      tags: ""

    # OR

    vault:
      address: ""
      prefix: ""
      authToken: ""
      authTokenSecretKey: ""
```

</details>

<details>
<summary>
Update syntax for other customizatons
</summary>

If you have further customizations in your V1 values.yaml file, move those over to your new values.yaml file, and update key names where appropriate.

- Change hyphenated V1 keys keys to camel case in V2. For example, when copying over `workload-launcher`, change it to `workloadLauncher`.

- Some keys have different names. For example, `orchestrator` is `containerOrchestrator` in V2.

Here is the full list of changes.

<HelmSyntaxConversion/>

</details>

<details>
<summary>
Convert `extraEnv` variables
</summary>

In previous versions of your values.yaml file, you might have specified a number of environment variables through `extraEnv`. Many (but not all) of these variables have a dedicated interface in Helm chart V2. For example, look at the following configuration, which tells `workload-launcher` to run pods in the `jobs` node group.

```yaml title="values.yaml using Helm chart V1"
workload-launcher:
  nodeSelector:
    type: static
  ## Pods spun up by the workload launcher will run in the 'jobs' node group.
  extraEnv:
    - name: JOB_KUBE_NODE_SELECTORS
      value: type=jobs
    - name: SPEC_JOB_KUBE_NODE_SELECTORS
      value: type=jobs
    - name: CHECK_JOB_KUBE_NODE_SELECTORS
      value: type=jobs
    - name: DISCOVER_JOB_KUBE_NODE_SELECTORS
      value: type=jobs
```

You can specify these values directly without using environment variables, achieving the same effect.

```yaml title="values.yaml using Helm chart V2"
global:
  jobs:
    kube:
      nodeSelector:
        type: jobs
      scheduling:
        check:
          nodeSelectors:
            type: jobs
        discover:
          nodeSelectors:
            type: jobs
        spec:
          nodeSelectors:
            type: jobs

workloadLauncher:
  nodeSelector:
    type: static
```

<EnvironmentVarConversion/>

</details>

## Manage Docker images

To get a manifest of the images used by Airbyte and abctl, run:

```bash
abctl images manifest
```

## Get abctl version information

To display version information about the abctl tool, run `abctl version`.

```bash
$ abctl version
version: v0.19.0
```

## Help and debugging

All abctl commands and sub-commands support two flags:

- `--help`: Displays help information, describing the available options for this command.
- `--verbose`: Enables verbose/debug output. This is useful when debugging unexpected behavior.

## Disable telemetry

You can turn off telemetry tracking on the abctl tool by setting the environment variable `DO_NOT_TRACK` to any value.

## Full abctl reference {#reference}

abctl has three commands: `local`, `images`, and `version`. Most commands have sub-commands and support various flags.

<details>
    <summary>`local`</summary>

    Local sub-commands are focused on managing the local Airbyte installation.
    
    <details>
        <summary>`credentials`</summary>

        Display the credentials required to login to the local Airbyte installation.

        When `abctl local install` is first executed, a random `password`, `client-id`, and `client-secret` are generated. Returns the `email`, `password`, `client-id`, and `client-secret` credentials. The `email` and  `password` are required to login to Airbyte. The `client-id` and `client-secret` are necessary to create an [Access Token for interacting with the Airbyte API](https://reference.airbyte.com/reference/createaccesstoken).

        `credentials` has the following flags.

        | Name       | Default | Description                               | Example          |
        | ---------- | ------- | ----------------------------------------- | ---------------- |
        | --email    | ""      | Changes the authentication email address. | you@example.com  |
        | --password | ""      | Changes the authentication password.      | MyStrongPassword |
    </details>

    <details>
    <summary>`deployments`</summary>

    Display kubernetes deployment information and allows for restarting a kubernetes deployment.

    `deployments` has the following flags.

    | Name      | Default | Description                       | Example |
    | --------- | ------- | --------------------------------- | ------- |
    | --restart | ""      | Restarts the provided deployment. | webapp  |

    </details>

    <details>
    <summary>`install`</summary>

    Installs a local Airbyte instance or updates an existing installation which was initially installed by `abctl`.

    Depending on your internet speed, `abctl local install` may take up to 30 minutes.

    `install` has the following flags.

    | Name                | Default | Description                                                                                                                                                                                                                                            | Example                    |
    | ------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------- |
    | --chart             | ""      | Path to chart.                                                                                                                                                                                                                                         | ./my-chart                 |
    | --chart-version     | latest  | Which Airbyte helm-chart version to install.                                                                                                                                                                                                          | 0.422.2                    |
    | --docker-email      | ""      | Docker email address to authenticate against `--docker-server`. Can also be specified by the environment-variable `ABCTL_LOCAL_INSTALL_DOCKER_EMAIL`.                                                                                               | user@example.com          |
    | --docker-password   | ""      | Docker password to authenticate against `--docker-server`. Can also be specified by the environment-variable `ABCTL_LOCAL_INSTALL_DOCKER_PASSWORD`.                                                                                                 | mypassword                 |
    | --docker-server     | ""      | Docker server to authenticate against. Can also be specified by the environment-variable `ABCTL_LOCAL_INSTALL_DOCKER_SERVER`.                                                                                                                       | docker.io                 |
    | --docker-username   | ""      | Docker username to authenticate against `--docker-server`. Can also be specified by the environment-variable `ABCTL_LOCAL_INSTALL_DOCKER_USERNAME`.                                                                                                 | myusername                 |
    | --insecure-cookies  | -       | Disables secure cookie requirements. Only set if using `--host` with an insecure (non `https`) connection.                                                                                                                                           | -                          |
    | --low-resource-mode | false   | Run Airbyte in low resource mode.                                                                                                                                                                                                                     | true                       |
    | --host              | ""      | FQDN where the Airbyte installation will be accessed. Default is to allow for all incoming traffic on port `--port`. Set this if the Airbyte installation needs a more restricted host configuration.                                              | airbyte.example.com        |
    | --no-browser        | -       | Disables launching the browser when installation completes. Useful to set in situations where no browser is available.                                                                                                                               | -                          |
    | --port              | 8000    | Port where the Airbyte installation will be accessed. Set this if port 8000 is already in use or if a different port is preferred.                                                                                                                   | 9000                       |
    | --secret            | ""      | **Can be set multiple times**. Creates a kubernetes secret based on the contents of the file provided. Useful when used in conjunction with `--values` for customizing installation.                                                                | ./my-secret.yaml           |
    | --values            | ""      | Helm values file to further customize the Airbyte installation.                                                                                                                                                                                       | ./values.yaml              |
    | --volume            | ""      | **Can be set multiple times**. Mounts additional volumes in the kubernetes cluster. Must be in the format of `<HOST_PATH>:<GUEST_PATH>`.                                                                                                             | /host/path:/container/path |

    </details>

    <details>
    <summary>`status`</summary>

    If an Airbyte installation exists, returns information regarding that installation.

    For example:
    ```
    $ abctl local status
    Existing cluster 'airbyte-abctl' found
    Found helm chart 'airbyte-abctl'
      Status: deployed
      Chart Version: 0.422.2
      App Version: 0.63.15
    Found helm chart 'ingress-nginx'
      Status: deployed
      Chart Version: 4.11.1
      App Version: 1.11.1
    Airbyte should be accessible via http://localhost:8000
    ```

    </details>

    <details>
    <summary>`uninstall`</summary>

    Uninstalls a local Airbyte instance.

    The data associated with the installed Airbyte instance will not be removed. This is done to allow Airbyte to be reinstalled at a later date with all the data preserved.

    `uninstall` has the following flags.

    | Name        | Default | Description                                                                    | Example |
    | ----------- | ------- | ------------------------------------------------------------------------------ | ------- |
    | --persisted | -       | Will remove all data for the Airbyte installation. This cannot be undone.     | -       |

    </details>

</details>

<details>
    <summary>`images`</summary>

    Manage images used by Airbyte and abctl.

    <details>
        <summary>`manifest`</summary>

        Display a manifest of images used by Airbyte and abctl.

        `manifest` has the following flags.

        | Name            | Default | Description                                                      | Example       |
        | --------------- | ------- | ---------------------------------------------------------------- | ------------- |
        | --chart         | ""      | Path to chart.                                                   | ./my-chart    |
        | --chart-version | latest  | Which Airbyte Helm chart version to install.                    | 0.422.2       |
        | --values        | ""      | Helm values file to further customize the Airbyte installation. | ./values.yaml |

    </details>

</details>

<details>
    <summary>`version`</summary>

    Displays version information about the `abctl` tool.

    For example:
    ```
    $ abctl version
    version: v0.19.0
    ```

</details>

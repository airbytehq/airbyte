# Troubleshooting abctl

This guide will help you navigate any issues with deploying Airbyte. This guide is intended for users of `abctl`.

## Common Errors

### Airbyte Bootloader failed to start

- Error: `pod airbyte-abctl-airbyte-bootloader failed`
- Github Discussion [#45458](https://github.com/airbytehq/airbyte/discussions/45458)
- Status: Investigating

The `airbyte-bootloader` is the first to start during the installation.
Version `>0.15.0` of `abctl` prints the service logs to make simpler to understand what is causing the issue.
Failures reasons are generally related to problem of `airbyte-bootloader` not able to connect to the `airbyte-db` service.

---

### Error Running Docker Command

- Error: `unable to create kind cluster: command "docker run --name airbyte-abctl-control-plane ..." failed with error: exit status 125`
- Github Issue [#45462](https://github.com/airbytehq/airbyte/issues/45462)
- Status: Investigating

We recommend that you copy and run the `docker run` command manually.
This may provide more meaningful error messages explaining why it is failing.
Additionally, verify that you can run Docker containers in general by starting with `docker run hello-world`.

```shell
unable to create kind cluster: command "docker run --name airbyte-abctl-control-plane
--hostname airbyte-abctl-control-plane --label io.x-k8s.kind.role=control-plane --privileged
--security-opt seccomp=unconfined --security-opt apparmor=unconfined --tmpfs /tmp --tmpfs /run
--volume /var --volume /lib/modules:/lib/modules:ro -e KIND_EXPERIMENTAL_CONTAINERD_SNAPSHOTTER
--detach --tty --label io.x-k8s.kind.cluster=airbyte-abctl --net kind --restart=on-failure:1
--init=false --cgroupns=private --volume /dev/mapper:/dev/mapper
--volume=/home/chang.kim/.airbyte/abctl/data:/var/local-path-provisioner --publish=0.0.0.0:8000:80/TCP
--publish=127.0.0.1:44776:6443/TCP -e KUBECONFIG=/etc/kubernetes/admin.conf kindest/node:v1.29.
4@sha256:3abb816a5b1061fb15c6e9e60856ec40d56b7b52bcea5f5f1350bc6e2320b6f8"
failed with error: exit status 125
```

---

### Failed to Init Node with `kubeadm`

- Error: `failed to init node with kubeadm`
- Github Issue [#44914](https://github.com/airbytehq/airbyte/issues/44914)
- Status: Investigating

We recommend that you copy and run the `docker run` command manually.
This may provide more meaningful error messages explaining why it is failing.
Running manually the sucessful output says kubeadm was able to join worker nodes.
Additionally, verify that you can run Docker containers in general by starting with `docker run hello-world`.

```shell
 unable to create kind cluster: failed to init node with kubeadm:
 command "docker exec --privileged airbyte-abctl-control-plane kubeadm init
  --skip-phases=preflight --config=/kind/kubeadm.conf --skip-token-print --v=6"
  failed with error: exit status 1
```

---

### Time Out Waiting for the Condition

- Error: `timed out waiting for the condition`

```shell
unable to install airbyte chart: unable to install helm: failed pre-install:
 1 error occurred: * timed out waiting for the condition
```

---

### Not able to ingress direct IP addresses

- Error: `must be a DNS name, not an IP address`
- Github Issue: [#110](https://github.com/airbytehq/abctl/pull/110)
- Status: **Solved**

:::tip
Upgrade to `abctl` version `>=0.15.0` default support exposing IP.
:::

```shell
unable to create ingress: Ingress.networking.k8s.io "ingress-abctl" is invalid:
spec.rules[2].host: Invalid value: "0.0.0.0": must be a DNS name, not an IP address
```

---

### Unable to Read Values from YAML file

- Error: `unable to read values from yaml file`

:::tip
Verify that you are in the correct directory or informing the path to the file correctly.
:::

```shell
unable to merge values with values file './values.yaml': unable to read values
from yaml file './values.yaml': failed to read file ./values.yaml: open ./values.yaml:
 no such file or directory
```

---

### Could not Create REST Config

- Error: `could not create rest config`

This error can happen when `abctl` does not have permission to create file and folders in your system.

```shell
unable to initialize local command: error communicating with kubernetes:
could not create rest config: stat /root/.airbyte/abctl/abctl.kubeconfig:
no such file or directory
```

---

### Failed to Create Patch Order in Patch List

- Error: `failed to create patch: The order in patch list`
- Github [#114](https://github.com/airbytehq/abctl/pull/114)
- Status: Fixing

This error can occur when installing using `abctl local install` and subsequently ran `abctl local install --low-resource-mode`.

```shell
unable to install airbyte chart: unable to install helm: failed to create patch:
The order in patch list: [map[name:JOB_MAIN_CONTAINER_CPU_REQUEST value:0]
map[name:JOB_MAIN_CONTAINER_CPU_REQUEST valueFrom:map[configMapKeyRef:
map[key:JOB_MAIN_CONTAINER_CPU_REQUEST name:airbyte-abctl-airbyte-env]]]
 map[name:JOB_MAIN_CONTAINER_CPU_LIMIT value:0] map[name:JOB_MAIN_CONTAINER_CPU_LIMIT
 valueFrom:map[configMapKeyRef:map[key:JOB_MAIN_CONTAINER_CPU_LIMIT
 name:airbyte-abctl-airbyte-env]]] map[name:JOB_MAIN_CONTAINER_MEMORY_REQUEST
 value:0] map[name:JOB_MAIN_CONTAINER_MEMORY_REQUEST
```

---

### Connection Refused

- Error: `connection refused`

```shell
unable to initialize local command: error communicating with kubernetes:
 unable to fetch kubernetes server version: Get "https://127.0.0.1:50124/version":
  dial tcp 127.0.0.1:[PORT]: connect: connection refused
```

---

### Resource Name May Not Be Empty

- Error: `unexpected error while handling the secret : resource name may not be empty`
- Github [#113](https://github.com/airbytehq/abctl/pull/113)
- Status: Solved

:::tip
Upgrade to version `>0.15.1`
:::

Version `0.15.0` had a bug when users have `secrets.yaml` file. You must upgrade your `abctl` to fix this issue.

---

## FAQ

### Using standard tools to interact with an Airbyte instance that was installed with `abctl`

`abctl` install Airbyte into a kind cluster on your local machine. If you'd like to interact directly with any of the underlying infrastructure, you can use standard tooling. You will need to make sure these tools are installed (or install them yourself). Any of these out of the box tools will work with an Airbyte instance installed with `abctl`.

If you want to interact with the pods or resources inside the cluster you can use [kubectl](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/) and [helm](https://helm.sh/). Just make sure you are pointing at the correct K8s configuration e.g. `kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig --namespace airbyte-abctl get pods`

[kind](https://kind.sigs.k8s.io/) is a tool for creating a K8s cluster using docker instead of having to install a local K8s cluster. You only need to think about kind if you want to make an adjustment to the cluster itself.

For more advanced interactions (e.g. loading custom docker containers), read more in [developing locally](../../contributing-to-airbyte/developing-locally#using-abctl-for-airbyte-development).

### Unable To Locate User Email

:::note
In `abctl` [v0.11.0](https://github.com/airbytehq/abctl/releases/tag/v0.11.0), support for basic-auth was removed (as basic-auth support was removed from the `Airbyte Platform` in [v0.63.11](https://github.com/airbytehq/airbyte-platform/releases/tag/v0.63.11), and replaced with a more secure randomly generated password. When logging into Airbyte, the email (provided during registration) should be automatically populated. Both the email and the randomly generated password can be fetched by running `abctl local credentials`.

Airbyte is aware of situations where the email is not be automatically populated and we are working on addressing this within the `abctl` tool. In the interim, some manually steps are required to retrieve the authentication email address when it is unknown.
:::

If the email address for authenticating is not automatically populated, you can set an email with the following command:

```
abctl local credentials --email <USER@COMPANY.EXAMPLE>
```

The password for this user can be retrieved by running `abctl local credentials`.

### Using Custom Connectors

In order to run a custom connector with an Airbyte instance that is running in kind, you must load the docker image of that connector into the cluster. A connector container can be loaded using the following command:

```
kind load docker-image <image-name>:<image-tag> -n airbyte-abctl
```

For more troubleshooting information review the troubleshooting section in [Uploading Customer Connectors](../../operator-guides/using-custom-connectors#troubleshooting)

### How do I connect from a container to a service on the host?

> The host has a changing IP address, or none if you have no network access. We recommend that you connect to the special DNS name host.docker.internal, which resolves to the internal IP address used by the host.

https://docs.docker.com/desktop/faqs/general/#how-do-i-connect-from-a-container-to-a-service-on-the-host

## Additional Resources

There are several channels for community support of local setup and deployment.

**GitHub Airbyte Forum's Getting Started FAQ:**

Search the questions others have asked or ask a new question of your own in the [GitHub forum](https://github.com/airbytehq/airbyte/discussions/categories/questions).

**Airbyte Knowledge Base:**

While support services are limited to Cloud and Enterprise customers, anyone may search the support team's [Help Center](https://support.airbyte.com/hc).

**Community Slack:**

Helpful channels for troubleshooting include:

- [#ask-community-for-troubleshooting](https://airbytehq.slack.com/archives/C021JANJ6TY): Where members of the Airbyte community can ask and answer questions.
- [#ask-ai](https://airbytehq.slack.com/archives/C01AHCD885S): For quick answers sourced from documentation and open support channels, you can have a chat with our virtual Airbyte assistant.

**Introductory Course:**

On Udemy, [The Complete Hands-on Introduction to Airbyte](https://www.udemy.com/course/the-complete-hands-on-introduction-to-airbyte/) is a convenient and hands-on introduction to Airbyte that includes setting up example source and destination configurations. You'll also go on to use it in conjunction with Apache Airflow, Snowflake, dbt, and more.

**Bug Reports:**

If you find an issue with the `abctl` command, please report it as a github
issue [here](https://github.com/airbytehq/airbyte/issues) with the type of `🐛 [abctl] Report an issue with the abctl tool`.

**Releases:**

To install a prior release of `abctl`, you can find the list of releases [here](https://github.com/airbytehq/abctl/releases/).

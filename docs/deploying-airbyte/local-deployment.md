# Local Deployment

:::warning
This tool is in active development. Airbyte strives to provide high quality, reliable software, however there may be
bugs or usability issues with this command. If you find an issue with the `abctl` command, please report it as a github
issue [here](https://github.com/airbytehq/airbyte/issues) with the type of "🐛 [abctl] Report an issue with the abctl tool".

:::

:::info
These instructions have been tested on MacOS, Windows, Ubuntu and Fedora.

This tool is intended to get Airbyte running as quickly as possible with no additional configuration necessary.
Additional configuration options may be added in the future, however, if you need additional configuration options now, use the
docker compose solution by following the instructions for the `run_ab_platform.sh` script [here](/deploying-airbyte/docker-compose).

:::

## Setup & launch Airbyte

:::info
Mac users can use Brew to install the `abctl` command

```bash
brew tap airbytehq/tap
brew install abctl
```

:::

- Install `Docker Desktop` \(see [instructions](https://docs.docker.com/desktop/install/mac-install/)\).
- After `Docker Desktop` is installed, you must enable `Kubernetes` \(see [instructions](https://docs.docker.com/desktop/kubernetes/)\).
- If you did not use Brew to install `abctl` then download the latest version of `abctl` from the [releases page](https://github.com/airbytehq/abctl/releases) and run the following command:

:::info
Mac users may need to use the finder and Open With > Terminal to run the `abctl` command. After the first run
users should be able to run the command from the terminal. Airbyte suggests mac users to use `brew` if it is available.

:::

```bash
./abctl local install
```

- Your browser should open to the Airbyte Application, if it does not visit [http://localhost](http://localhost)
- You will be asked for a username and password. By default, that's username `airbyte` and password `password`. You can set these values through command line flags or environment variables. For example, to set the username and password to `foo` and `bar` respectively, you can run the following command:

```bash
./abctl local install --username foo --password bar

# Or as Environment Variables
ABCTL_LOCAL_INSTALL_PASSWORD=foo
ABCTL_LOCAL_INSTALL_USERNAME=bar
```

- Start moving some data!

## Troubleshooting

If you have any questions about the local setup and deployment process, head over to our [Getting Started FAQ](https://github.com/airbytehq/airbyte/discussions/categories/questions) on our Airbyte Forum that answers the following questions and more:

- How long does it take to set up Airbyte?
- Where can I see my data once I've run a sync?
- Can I set a start time for my sync?

If you encounter any issues, check out [Getting Support](/community/getting-support) documentation
for options how to get in touch with the community or us.

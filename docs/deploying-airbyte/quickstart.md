# Airbyte Quickstart

Airbyte has a single binary tool called `abctl` which can be used to quickly standup Airbyte.

## Setup & launch Airbyte

- Install `Docker Desktop` \(see [instructions](https://docs.docker.com/desktop/install/mac-install/)\).
- Download the latest version of `abctl` from the [releases page](https://github.com/airbytehq/abctl/releases)

:::info
Mac users can use Brew to install the `abctl` command

```bash
brew tap airbytehq/tap
brew install abctl
```

:::

Then you can run Airbyte with the following command:

```bash
abctl local install
```

- Your browser should open to the Airbyte Application, if it does not visit [http://localhost:8000](http://localhost:8000)
- You will be asked for a username and password. By default, that's username `airbyte` and password `password`. You can set these values through command line flags or environment variables. For example, to set the username and password to `foo` and `bar` respectively, you can run the following command:

```bash
abctl local install --username foo --password bar

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

If you find an issue with the `abctl` command, please report it as a github
issue [here](https://github.com/airbytehq/airbyte/issues) with the type of "🐛 [abctl] Report an issue with the abctl tool".

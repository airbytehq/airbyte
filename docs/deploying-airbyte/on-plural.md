# On Plural (Beta)

## Overview

Plural is a unified application deployment platform that makes it easy to run open-source software on Kubernetes. It aims to make applications as portable as possible, without sacrificing the ability for the users to own the applications they desire to use.

## Getting Started

First, create an account on https://app.plural.sh.  This is simply to track your installations and allow for the delivery of automated upgrades, you will not be asked to provide any infrastructure credentials or sensitive information.

Then, install the Plural CLI by following steps 1, 2, and 3 of the instructions [here](https://docs.plural.sh/getting-started). Through this, you will also configure your cloud provider and the domain name under which your application will be deployed to.

Then create a fresh Git repo to store your Plural installation and from within the repo, run:

```bash
plural init
```

This configures your installation and cloud provider for the repo. You're now ready to install Airbyte on your Plural repo!

## Installing Airbyte

To install Airbyte on your Plural repo, simply run:

```bash
plural bundle install airbyte airbyte-aws
```

Plural's Airbyte distribution currently has support for AWS, GCP and Azure set up and ready to go, so feel free to pick whichever best fits your infrastructure.

The CLI will prompt you to choose whether or not you want to use Plural OIDC, which means you're using Plural as your identity provider for SSO.

After this, run:

```bash
plural build
plural deploy --commit "deploying airbyte"
```

## Adding the Plural Console

To make management of your installation as simple as possible, we recommend installing the Plural Console.  The console provides tools to manage resource scaling, receiving automated upgrades and getting out-of-the-box dashboarding and log aggregation. This can be done using the exact same process as above:

```bash
plural bundle install console console-aws
plural build
plural deploy --commit "deploying the console too"
```

## Accessing your Airbyte Installation

Now, just head over to airbyte.SUBDOMAIN_NAME.onplural.sh to access the Airbyte UI.

## Accessing your Console Installation

To monitor and manage your Airbyte installation, head over to the Plural Console at console.YOUR_ORGANIZATION.onplural.sh (or whichever subdomain you chose).

## Troubleshooting

If you have any issues with installing Airbyte on Plural, feel free to jump into our [discord](https://discord.gg/bEBAMXV64s) and we can help you out.

If you'd like to request any new features for our Airbyte install, feel free to open an issue or PR at https://github.com/pluralsh/plural-artifacts.

## Further Reading

To learn more about what you can do with Plural and more advanced uses of the platform, feel free to dive deeper into our docs [here](https://docs.plural.sh)

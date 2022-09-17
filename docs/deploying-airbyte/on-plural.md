# On Plural

## Overview

[Plural](https://www.plural.sh/) is a free, open-source, unified application deployment platform that makes it easy to run open-source software on Kubernetes. It aims to make applications as portable as possible, without sacrificing the ability for the users to own the applications they desire to use.

## Getting Started

:::tip
If you'd prefer to follow along with a video, check out the Plural Airbyte deployment guide video [here](https://youtu.be/suvTJyJ6PzI)
:::

First, create an account on [https://app.plural.sh](https://app.plural.sh).  This is simply to track your installations and allow for the delivery of automated upgrades, you will not be asked to provide any infrastructure credentials or sensitive information.

Then, install the Plural CLI by following steps 1, 2, and 3 of the instructions [here](https://docs.plural.sh/getting-started). Through this, you will also configure your cloud provider and the domain name under which your application will be deployed to.

We now need a Git repository to store your Plural configuration in. This will also contain the Helm and Terraform files that Plural will autogenerate for you.

You now have two options:
- Run `plural init` in any directory to let Plural initiate an OAuth workflow to create a Git repo for you.
- Create a Git repo manually, clone it down and run `plural init` inside it.

Running `plural init` will configure your installation and cloud provider for the repo. You're now ready to install Airbyte on your Plural repo!

## Installing Airbyte

To install Airbyte on your Plural repo, simply run:

```bash
plural bundle install airbyte $CONSOLE_BUNDLE_NAME
```

To find the console bundle name for your cloud provider, run:

```bash
plural bundle list airbyte
```

For example, this is what it looks like for AWS:

```bash
plural bundle install airbyte airbyte-aws
```

Plural's Airbyte distribution currently has support for AWS, GCP and Azure set up and ready to go, so feel free to pick whichever best fits your infrastructure.

The CLI will prompt you to choose whether or not you want to use Plural OIDC. [OIDC](https://openid.net/connect/) allows you to login to the applications you host on Plural with your login to [app.plural.sh](https://app.plural.sh), acting as an SSO provider.

After this, run:

```bash
plural build
plural deploy --commit "deploying airbyte"
```

## Adding the Plural Console

To make management of your installation as simple as possible, we recommend installing the Plural Console.  The console provides tools to manage resource scaling, receiving automated upgrades, dashboards tailored to your Airbyte installation, and log aggregation. This can be done using the exact same process as above:

```bash
plural bundle install console console-aws
plural build
plural deploy --commit "deploying the console too"
```

## Accessing your Airbyte Installation

Now, just head over to `airbyte.SUBDOMAIN_NAME.onplural.sh` to access the Airbyte UI.

## Accessing your Console Installation

To monitor and manage your Airbyte installation, head over to the Plural Console at `console.YOUR_ORGANIZATION.onplural.sh` (or whichever subdomain you chose).

## Advanced Use Cases

### Running with External Airflow

If you have an Airflow instance external to the Plural Kubernetes cluster with your Airbyte installation, you can still have Airflow manage the Airbyte installation. This happens because Basic Auth setup is required for external authentication - Plural OIDC is not sufficient here.

In your `context.yaml` file located at the root of your Plural installation, create a user with Basic Auth for Airbyte. Then on your Airbyte Airflow connector, use the following URL template:

```
https://username:password@airbytedomain
```

## Troubleshooting

If you have any issues with installing Airbyte on Plural, feel free to join our [Discord Community](https://discord.gg/bEBAMXV64s) and we can help you out.

If you'd like to request any new features for our Airbyte installation, feel free to open an issue or PR at https://github.com/pluralsh/plural-artifacts.

## Further Reading

To learn more about what you can do with Plural and more advanced uses of the platform, feel free to dive deeper into our docs [here.](https://docs.plural.sh)

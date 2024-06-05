# Deploy Airbyte on Plural

:::tip
If you'd prefer to follow along with a video, check out the Plural Airbyte deployment guide video [here](https://youtu.be/suvTJyJ6PzI)
:::

## Getting started

1. Create an account on [https://app.plural.sh](https://app.plural.sh).
2. Install the Plural CLI by following steps 1, 2, and 3 of the instructions [here](https://docs.plural.sh/getting-started). Through this, you will also configure your cloud provider and the domain name under which your application will be deployed to.

We now need a Git repository to store your Plural configuration in. This will also contain the Helm and Terraform files that Plural will autogenerate for you.

You have two options:

- Run `plural init` in any directory to let Plural initiate an OAuth workflow to create a Git repo for you.
- Create a Git repo manually, clone it, and run `plural init` inside it.

Running `plural init` will configure your installation and cloud provider for the repo.

## Installing Airbyte

To install Airbyte on your Plural repo, run:

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

Plural's Airbyte distribution currently has support for AWS, GCP and Azure. Select the Cloud that best fits your infrastructure.

The CLI prompts you to choose whether or not you want to use Plural OIDC. [OIDC](https://openid.net/connect/) allows you to login to the applications you host on Plural with your login to [app.plural.sh](https://app.plural.sh), acting as an SSO provider.

After this, run:

```bash
plural build
plural deploy --commit "deploying airbyte"
```

## Adding the Plural Console

To make management of your installation as simple as possible, we recommend installing the Plural Console. The console provides tools to manage resource scaling, receiving automated upgrades, dashboards tailored to your Airbyte installation, and log aggregation. Run:

```bash
plural bundle install console console-aws
plural build
plural deploy --commit "deploying the console too"
```

## Accessing your Airbyte Installation

Navigate to `airbyte.SUBDOMAIN_NAME.onplural.sh` to access the Airbyte UI.

## Accessing your Console Installation

To monitor and manage your Airbyte installation, navigate to the Plural Console at `console.YOUR_ORGANIZATION.onplural.sh` (or whichever subdomain you chose).

## Advanced Use Cases

### Running with External Airflow

If you have an Airflow instance external to the Plural Kubernetes cluster with your Airbyte installation, you can still have Airflow manage the Airbyte installation. This happens because Basic Auth setup is required for external authentication - Plural OIDC is not sufficient here.

In your `context.yaml` file located at the root of your Plural installation, create a user with Basic Auth for Airbyte. Then on your Airbyte Airflow connector, use the following URL template:

```
https://username:password@airbytedomain
```

## Troubleshooting

If you have any issues with installing Airbyte on Plural, join Plural's [Discord Community](https://discord.gg/bEBAMXV64s).

If you'd like to request any new features for our Airbyte installation, open an issue or PR at https://github.com/pluralsh/plural-artifacts.

## Further Reading

To learn more about Plural, refer to the [Plural documentation](https://docs.plural.sh)

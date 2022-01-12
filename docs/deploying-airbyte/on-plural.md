# On Plural

## Overview

Plural is a unified application deployment platform that makes it easy to run open-source software on Kubernetes. It aims to make applications as portable as possible, without sacrificing the ability for the users to own the applications they desire to use.

## Getting Started

First, install Plural and the Plural CLI by following steps 1, 2, and 3 of the instructions [here](https://docs.plural.sh/getting-started). Through this, you will also configure your cloud provider and the domain name under which your
application will be deployed to.

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

The CLI will prompt you to choose whether or not you want to use Plural OIDC, which means you're using Plural as your identity provider for SSO.

After this, run:

```bash
plural build
plural deploy --commit "Initial Deploy."
```

## Accessing your Airbyte Installation

Now, just head over to airbyte.SUBDOMAIN_NAME.onplural.sh to access the Airbyte UI.

## Monitoring your Installation

To monitor and manage your Airbyte installation, head over to the Plural control panel at console.YOUR_ORGANIZATION.onplural.sh.

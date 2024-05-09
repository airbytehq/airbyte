# Connector Development

There are two types of connectors in Airbyte: Sources and Destinations. Connectors can be built in
any programming language, as long as they're built into docker images that implement the
[Airbyte specification](../understanding-airbyte/airbyte-protocol.md).

Most database sources and destinations are written in Java. API sources and destinations are written
in Python using the [Low-code CDK](config-based/low-code-cdk-overview.md) or
[Python CDK](cdk-python/).

If you need to build a connector for an API Source, start with Connector Builder. It'll be enough
for most use cases. If you need help with connector development, we offer premium support to our
open-source users, [talk to our team](https://airbyte.com/talk-to-sales-premium-support) to get
access to it.

### Connector Builder

The [connector builder UI](connector-builder-ui/overview.md) is based on the low-code development
framework below and allows to develop and use connectors without leaving the Airbyte web UI. No
local developer environment required.

### Low-code Connector-Development Framework

You can use the [low-code framework](config-based/low-code-cdk-overview.md) to build source
connectors for HTTP API sources. Low-code CDK is a declarative framework that provides a YAML schema
to describe your connector without writing any Python code, but allowing you to use custom Python
components if required.

### Python Connector-Development Kit \(CDK\)

You can build a connector in Python with the [Airbyte CDK](cdk-python/). Compared to the low-code
CDK, the Python CDK is more flexible, but building the connector will be more involved. It provides
classes that work out of the box for most scenarios, and Airbyte provides generators that make the
connector scaffolds for you. Here's a guide for
[building a connector in Python CDK](tutorials/custom-python-connector/0-getting-started.md).

### Community maintained CDKs

The Airbyte community also maintains some CDKs:

- The [Typescript CDK](https://github.com/faros-ai/airbyte-connectors) is actively maintained by
  Faros.ai for use in their product.
- The [Airbyte Dotnet CDK](https://github.com/mrhamburg/airbyte.cdk.dotnet) in C#.

:::note
Before building a new connector, review
[Airbyte's data protocol specification](../understanding-airbyte/airbyte-protocol.md).
:::

## Adding a new connector

The easiest way to make and start using a connector in your workspace is by using the
[Connector Builder](connector-builder-ui/overview.md).

If you're writing your connector in Python or low-code CDK, use the generator to get the project
started:

```bash
cd airbyte-integrations/connector-templates/generator
./generate.sh
```

and choose the relevant template by using the arrow keys. This will generate a new connector in the
`airbyte-integrations/connectors/<your-connector>` directory.

Search the generated directory for "TODO"s and follow them to implement your connector. For more
detailed walkthroughs and instructions, follow the relevant tutorial:

- [Building a HTTP source with the CDK](tutorials/custom-python-connector/0-getting-started.md)
- [Building a Java destination](tutorials/building-a-java-destination.md)

As you implement your connector, make sure to review the
[Best Practices for Connector Development](best-practices.md) guide.

## Updating an existing connector

The steps for updating an existing connector are the same as for building a new connector minus the
need to use the autogenerator to create a new connector. Therefore the steps are:

1. Iterate on the connector to make the needed changes
2. Run tests
3. Add any needed docs updates
4. Create a PR and get it reviewed and merged.

The new version of the connector will automatically be published in Cloud and OSS registries when
the PR is merged.

## Publishing a connector

Once you've finished iterating on the changes to a connector as specified in its `README.md`, follow
these instructions to ship the new version of the connector with Airbyte out of the box.

1. Bump the docker image version in the [metadata.yaml](connector-metadata-file.md) of the
   connector.
2. Submit a PR containing the changes you made.
3. One of Airbyte maintainers will review the change in the new version and make sure the tests are
   passing.
4. You our an Airbyte maintainer can merge the PR once it is approved and all the required CI checks
   are passing you.
5. Once the PR is merged the new connector version will be published to DockerHub and the connector
   should now be available for everyone who uses it. Thank you!

### Updating Connector Metadata

When a new (or updated version) of a connector is ready, our automations will check your branch for
a few things:

- Does the connector have an icon?
- Does the connector have documentation and is it in the proper format?
- Does the connector have a changelog entry for this version?
- The [metadata.yaml](connector-metadata-file.md) file is valid.

If any of the above are failing, you won't be able to merge your PR or publish your connector.

Connector icons should be square SVGs and be located in
[this directory](https://github.com/airbytehq/airbyte/tree/master/airbyte-config-oss/init-oss/src/main/resources/icons).

Connector documentation and changelogs are markdown files living either
[here for sources](https://github.com/airbytehq/airbyte/tree/master/docs/integrations/sources), or
[here for destinations](https://github.com/airbytehq/airbyte/tree/master/docs/integrations/destinations).

## Using credentials in CI

In order to run integration tests in CI, you'll often need to inject credentials into CI. There are
a few steps for doing this:

1. **Place the credentials into Google Secret Manager(GSM)**: Airbyte uses a project 'Google Secret
   Manager' service as the source of truth for all CI secrets. Place the credentials **exactly as
   they should be used by the connector** into a GSM secret
   [here](https://console.cloud.google.com/security/secret-manager?referrer=search&orgonly=true&project=dataline-integration-testing&supportedpurview=organizationId)
   i.e.: it should basically be a copy paste of the `config.json` passed into a connector via the
   `--config` flag. We use the following naming pattern:
   `SECRET_<capital source OR destination name>_CREDS` e.g: `SECRET_SOURCE-S3_CREDS` or
   `SECRET_DESTINATION-SNOWFLAKE_CREDS`.
2. **Add the GSM secret's labels**:
   - `connector` (required) -- unique connector's name or set of connectors' names with '\_' as
     delimiter i.e.: `connector=source-s3`, `connector=destination-snowflake`
   - `filename` (optional) -- custom target secret file. Unfortunately Google doesn't use '.' into
     labels' values and so Airbyte CI scripts will add '.json' to the end automatically. By default
     secrets will be saved to `./secrets/config.json` i.e: `filename=config_auth` =>
     `secrets/config_auth.json`
3. **Save a necessary JSON value**
   [Example](https://user-images.githubusercontent.com/11213273/146040653-4a76c371-a00e-41fe-8300-cbd411f10b2e.png).
4. That should be it.

#### Access CI secrets on GSM

Access to GSM storage is limited to Airbyte employees. To give an employee permissions to the
project:

1. Go to the permissions'
   [page](https://console.cloud.google.com/iam-admin/iam?project=dataline-integration-testing)
2. Add a new principal to `dataline-integration-testing`:

- input their login email
- select the role `Development_CI_Secrets`

3. Save

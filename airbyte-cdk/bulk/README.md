# Bulk CDK

The Bulk CDK is the "new java CDK" that's currently incubating.
As the name suggests, its purpose is to help develop connectors which extract or load data in bulk.
The Bulk CDK is written in Kotlin and uses the Micronaut framework for dependency injection.

## Structure

The Bulk CDK consists of a _core_ and a bunch of _toolkits_.

### Core

The _core_ consists of the Micronaut entry point and other objects which are expected in
connectors built using this CDK.

The core is broken down into multiple gradle projects; for example the core functionality for
building sources is in `extract`.

Following up on that example, the expectation for a source connector is that it will use all the
interfaces and implementations in `extract` unless it has a very good reason not to.
There is plenty of value in having all source connectors behave predictably.

### Toolkits

The _toolkits_ consist of optional modules which contain objects which are common across
multiple (but by no means all) connectors.

For example, there's an `extract-jdbc` toolkit to help build source connectors which extract data
using the JDBC API.
The expectation for a toolkit is that it provides naive implementations of core interfaces.
These implementations will be thoroughly tested inside the CDK to serve as a baseline of
functionality; however the connector may (and in fact often should!) replace parts of these.

Following up on the example of `extract-jdbc`, a source connector needs to implement SQL query
generation interfaces and, for schema discovery, may prefer to query system tables directly
instead of relying on the generic JDBC metadata methods.

## Dependencies

The Bulk CDK gradle build relies heavily on so-called [BOM dependencies](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html#bill-of-materials-bom-poms).
This pattern is strongly encouraged to keep transitive version conflicts to a minimum.  This is beneficial for many reasons, including reproducible builds and a good security posture. 

Consider for example the whole Jackson ecosystem.
Using a BOM allows us to add specific Jackson dependencies without having to figure out which
version number to use.
This has some pleasant ripple-effects:

- When the need comes to bump the version, there's only one version number to bump and that's in
  the BOM import.
  Consequently, the declared version has a much higher chance of being the effective version
  picked by gradle during dependency resolution.

- The BOM import is re-exported by the `bulk-cdk-core-base` artifact meaning that the rest of the
  CDK as well as connectors don't need to worry about Jackson version numbers either.

It gets better when multiple BOMs are involved.
Consider for example Micronaut and Jackson: Micronaut also depends on Jackson.
This can (and will!) cause dependency version conflicts; these are much easier to resolve by
reconciling just two BOM versions.

While BOMs are undoubtedly useful, let's still try to keep external dependencies to a minimum
outside of tests.
Less dependencies, less problems.

## Developing

Perhaps the most striking difference with the legacy java CDK from a connector DX perspective is
that there are no facilities equivalent to `useLocalCdk = true`.

This is deliberate and the intention here is to force the testing of CDK functionality to remain
in the CDK.
Recall that this is too often not the case in the legacy java CDK because it's simply not possible
to do so there.

The Bulk CDK is different.
Dependency injection makes it possible to mock concrete implementation behavior realistically
enough that Bulk CDK tests have entire fake connectors defined inside of them.

There's no reason now not to first make changes to the CDK and publish those, and only then make
downstream changes to a connector.

If there's truly a need to develop both simultaneously, then the way to go may be to:
1. do experimental development in the connector, keeping the CDK- and the connector-specific code
   separate;
2. once the CDK-specific code is reasonably mature, hoist it into the Bulk CDK and test it there;
3. finally, publish those changes and have the connector depend on the latest Bulk CDK version.

## Publishing

While the CDK is incubating, its published version numbers are 0.X where X is the _build number_.
This build number is monotonically increasing and is based on the maximum version value found on
the [maven repository that the jars are published to](https://airbyte.mycloudrepo.io/public/repositories/airbyte-public-jars/io/airbyte/bulk-cdk/).

Artifact publication happens via a [github workflow](../../.github/workflows/publish-bulk-cdk.yml)
which gets triggered by any push to the master branch, i.e. after merging a pull request.

From a contributor's perspective, this means that there's no need to worry about versions or
changelogs.
From a client's perspective, just always use the latest version.

Once the incubation period winds down and the CDK stabilizes, we can start thinking about contracts,
semantic versioning, and so forth; but not until then.

## Licensing

The license for the Bulk CDK is Elastic License 2.0, as specified by the LICENSE file in the root
of this git repository.

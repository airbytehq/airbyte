# Bulk CDK

The Bulk CDK is the "new java CDK" that's currently incubating.
It's written in Kotlin and consists of a _core_ and a bunch of _toolkits_:
- The _core_ consists of the Micronaut entry point and other objects which are expected in
  connectors built using this CDK.
- The _toolkits_ consist of optional modules which contain objects which are common across
  multiple (but by no means all) connectors.

While the CDK is incubating, its published version numbers are 0.X where X is monotonically
increasing based on the maximum version value found on the maven repository that the jars are
published to: https://airbyte.mycloudrepo.io/public/repositories/airbyte-public-jars/io/airbyte/bulk-cdk/

Jar publication happens via a github workflow triggered by pushes to the master branch, i.e. after
merging a pull request.

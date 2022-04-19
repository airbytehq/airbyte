# Generating Seed Connector Specs

The catalog of seeded connector definitions is stored and manually updated in the `airbyte-config/init/src/main/resources/seed/*_definitions.yaml`
files. These manually-maintained connector definitions intentionally _do not_ contain the connector specs, in an effort to keep these files
human-readable and easily-editable, and because specs can be automatically fetched.

This automatic fetching of connector specs is the goal of the SeedConnectorSpecGenerator. This class reads the connector definitions in
the `airbyte-config/init/src/main/resources/seed/*_definitions.yaml` files, fetches the corresponding specs from the GCS bucket cache, and writes the
specs to the `airbyte-config/init/src/main/resources/seed/*_specs.yaml` files. See the
[SeedConnectorSpecGenerator](src/main/java/io/airbyte/config/specs/SeedConnectorSpecGenerator.java) class for more details.

Therefore, whenever a connector definition is updated in the `airbyte-config/init/src/main/resources/seed/*_definitions.yaml` files, the
SeedConnectorSpecGenerator should be re-ran to generate the updated connector specs files. To do so,
run `./gradlew :airbyte-config:init:processResources`, or just build the platform project, and commit the changes to your PR. If you do not do this,
the build in the CI will fail because there will be a diff in the generated files as you have not checked in the changes that were applied by the
generator.

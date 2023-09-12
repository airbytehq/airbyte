#!/bin/bash
#
# Files not covered by the migration (copy these in manually):
# - airbyte-cdk/java/airbyte-cdk/_temp_migration_script.sh (this script)
# - airbyte-cdk/java/airbyte-cdk/build.gradle
# - buildSrc/src/main/groovy/airbyte-java-cdk.gradle
# - settings.gradle
#
# Commits to cherry pick:
# - eed850eafd6e2fb37b4ca7b5b3fd63ae237a2780 - add cdk gradle plugin to connectors
# - ceedc270b150aa4b532a8f42e8541880c9041312 - cleanup removed gradle refs
# - 1424b5f144378ac7532ae1a2e41c9f3d270169e7 - additional build.gradle fixes on connectors
#
# This file is an audit and automation tool for the CDK migration itself.
# It may be deleted befor the PR is merged.
#
# Usage:
#   MIGRATE_SH=./airbyte-cdk/java/airbyte-cdk/_temp_migration_script.sh
#   $MIGRATE_SH [<OLD_PACKAGE_ROOT>] ['asTestFixture']
#   E.g.
#   $MIGRATE_SH airbyte-db/db-lib
#   $MIGRATE_SH airbyte-integrations/bases/base-typing-deduping-test asTestFixture
#   ...
#   If OLD_PACKAGE_ROOT is not provided, we will loop through all known directories.
#
# Post-run cleanup stesps:
# - Find and delete references to the moved packages.
# - Add the new airbyte-java-connector plugin to connectors' build.gradle files.
# - Search-and-replace:
#   - Within ./airbyte-cdk/java/airbyte-cdk/**/*.java:
#     - Find:         `package io.airbyte`
#     - Replace with: `package io.airbyte.cdk`
#   - Within ./airbyte-cdk/java/airbyte-cdk/**/*.java (because the above is not idempotent):
#     - Find:         `package io.airbyte.cdk.cdk`
#     - Replace with: `package io.airbyte.cdk`
#   - Find all the packages that were moved, and name them in a way that is specific to the CDK inclusions:
#     - Find (regex): `io.airbyte...` # Everything that now shows up with a search for `package io.airbyte.cdk`
#                      io.airbyte.cdk.db
#                      io.airbyte.cdk.integrations.base
#                      io.airbyte.cdk.integrations.debezium
#                      io.airbyte.cdk.integrations.destination.NamingConventionTransformer
#                      io.airbyte.cdk.integrations.destination.StandardNameTransformer
#                      io.airbyte.cdk.integrations.destination.jdbc
#                      io.airbyte.cdk.integrations.destination.normalization
#                      io.airbyte.cdk.integrations.destination.record_buffer
#                      io.airbyte.cdk.integrations.destination.buffered_stream_consumer
#                      io.airbyte.cdk.integrations.destination.dest_state_lifecycle_manager
#                      io.airbyte.cdk.integrations.destination.staging
#                      io.airbyte.cdk.integrations.destination_async
#                      io.airbyte.cdk.integrations.source.jdbc
#                      io.airbyte.cdk.integrations.source.relationaldb
#                      io.airbyte.cdk.integrations.util
#                      io.airbyte.cdk.integrations.BaseConnector
#                      io.airbyte.cdk.test.utils
#            Warning: these packages all share the `io.airbyte.integrations.destination.s3` package name prefix:
#                      `base-java-s3`
#                      `destination-s3`
#                      `s3-destination-base-integration-test`
#            These S3 packages refs must be fixed manually without a global search/replace.
#                      io.airbyte.cdk.integrations.destination.s3.avro
#                      io.airbyte.cdk.integrations.destination.s3.constant
#                      io.airbyte.cdk.integrations.destination.s3.credential
#                      io.airbyte.cdk.integrations.destination.s3.csv
#                      io.airbyte.cdk.integrations.destination.s3.jsonl
#                      io.airbyte.cdk.integrations.destination.s3.parquet
#                      io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
#                      io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants;
#                      io.airbyte.cdk.integrations.destination.s3.S3Format;
#                      io.airbyte.cdk.integrations.destination.s3.S3FormatConfig
#                      io.airbyte.cdk.integrations.destination.s3.StorageProvider
#                      io.airbyte.cdk.integrations.destination.s3.template
#                      io.airbyte.cdk.integrations.destination.s3.util
#                      io.airbyte.cdk.integrations.destination.s3.writer
#           You can use this regex pattern to find and replace each one:
#              Find: io\.airbyte\.integrations\.destination\.s3\.(avro|constant|credential|csv|jsonl|parquet|S3DestinationConfig|S3DestinationConstants|S3Format|S3FormatConfig|StorageProvider|template|util|writer)\b
#              Replace: io.airbyte.cdk.integrations.destination.s3.$1
#            Also - be careful about word boundaries because this also exists with the same prefix:
#                       `...destination.s3_glue`
#   - Within rest of repo:
#     - Find (regex) based on the above list:
#         io\.airbyte\.(db|integrations\.base|integrations\.debezium|integrations\.destination\.NamingConventionTransformer|integrations\.destination\.StandardNameTransformer|integrations\.destination\.jdbc|integrations\.destination\.record_buffer|integrations\.destination\.normalization|integrations\.destination\.buffered_stream_consumer|integrations\.destination\.dest_state_lifecycle_manager|integrations\.destination\.staging|integrations\.destination_async|integrations\.source\.jdbc|integrations\.source\.relationaldb|integrations\.util|integrations\.BaseConnector|test\.utils)
#     - Replace with: io.airbyte.cdk.$1
#     - Exclude files: _temp_migration_script.sh,*.html,build,bin
# - Replace references to the moved packages with the new package names.
#
# Other notes:
# - This script is idempotent. It should become a no-op if run to completion.
# - The "typing_deduping" and "typing_deduping_test" subpackages are special cases. They migrated from different directories while being declared as the same package name: "io.airbyte.integrations.destination.typing_deduping".
# - Certain tasks may fail due to missing image integrations-base-java:dev. Rename Dockerfile to Dockerfile.bak to work around this.

# If no source directory is specified, this script will invoke itself for all known directory migrations:
if [ -z "$1" ]; then
  echo "No source directory specified. Running for all known directories..."
  MIGRATE_SH=$0

  # Core capabilities:
  $MIGRATE_SH airbyte-db/db-lib
  $MIGRATE_SH airbyte-integrations/bases/base-java
  $MIGRATE_SH airbyte-integrations/bases/base-java-s3
  $MIGRATE_SH airbyte-integrations/bases/base-typing-deduping
  $MIGRATE_SH airbyte-integrations/connectors/source-relational-db
  $MIGRATE_SH airbyte-integrations/bases/bases-destination-jdbc

  # Hybrid projects: capabilities plus test fixtures:
  $MIGRATE_SH airbyte-integrations/bases/debezium
  $MIGRATE_SH airbyte-integrations/connectors/source-jdbc

  # Test fixture projects:
  $MIGRATE_SH airbyte-integrations/bases/base-typing-deduping-test asTestFixture
  $MIGRATE_SH airbyte-integrations/bases/s3-destination-base-integration-test asTestFixture
  $MIGRATE_SH airbyte-integrations/bases/standard-destination-test asTestFixture
  $MIGRATE_SH airbyte-integrations/bases/standard-source-test asTestFixture
  $MIGRATE_SH airbyte-integrations/bases/base-standard-source-test-file asTestFixture
  $MIGRATE_SH airbyte-test-utils
  exit 0
fi

# Change these two lines for each new subpackage to move
OLD_PACKAGE_ROOT="$1"
# Get old project name from the OLD_PACKAGE_ROOT:
OLD_PROJECT_NAME=$(echo "$OLD_PACKAGE_ROOT" | sed 's/.*\/\(.*\)/\1/')

# Store the second value as "FLAG" if it exists
FLAG="$2"

# Declare source directories
OLD_MAIN_PATH="$OLD_PACKAGE_ROOT/src/main/java/io/airbyte"
OLD_TEST_PATH="$OLD_PACKAGE_ROOT/src/test/java/io/airbyte"
OLD_INTEGTEST_PATH="$OLD_PACKAGE_ROOT/src/test-integration/java/io/airbyte"
OLD_TESTFIXTURE_PATH="$OLD_PACKAGE_ROOT/src/testFixtures/java/io/airbyte"
OLD_MAIN_RESOURCES_PATH="$OLD_PACKAGE_ROOT/src/main/resources"
OLD_TEST_RESOURCES_PATH="$OLD_PACKAGE_ROOT/src/test/resources"
OLD_INTEGTEST_RESOURCES_PATH="$OLD_PACKAGE_ROOT/src/test-integration/resources"

# Declare destination directories
CDK_ROOT="airbyte-cdk/java/airbyte-cdk"
DEST_MAIN_PATH="$CDK_ROOT/src/main/java/io/airbyte/cdk"
DEST_TEST_PATH="$CDK_ROOT/src/test/java/io/airbyte/cdk"
DEST_INTEGTEST_PATH="$CDK_ROOT/src/test-integration/java/io/airbyte/cdk"
DEST_TESTFIXTURE_PATH="$CDK_ROOT/src/testFixtures/java/io/airbyte/cdk"
DEST_MAIN_RESOURCES_PATH="$CDK_ROOT/src/main/resources/$OLD_PROJECT_NAME"
DEST_TEST_RESOURCES_PATH="$CDK_ROOT/src/test/resources/$OLD_PROJECT_NAME"
DEST_INTEGTEST_RESOURCES_PATH="$CDK_ROOT/src/test-integration/resources/$OLD_PROJECT_NAME"
REMNANTS_ARCHIVE_PATH="airbyte-cdk/java/airbyte-cdk/archive/$OLD_PROJECT_NAME"

# Check if flag is 'asTestFixture'. If so, send 'main/java' to 'testFixtures/java':
if [ "$FLAG" = "asTestFixture" ]; then
  DEST_MAIN_PATH="$DEST_TESTFIXTURE_PATH"
fi

declare -a PATH_DESC=(  "main classes"   "main test classes" "integ test classes"   "test fixtures"          "main resources"            "test resources"            "integ test resources"           "remnamts to archive" )
declare -a SOURCE_DIRS=("$OLD_MAIN_PATH" "$OLD_TEST_PATH"    "$OLD_INTEGTEST_PATH"  "$OLD_TESTFIXTURE_PATH"  "$OLD_MAIN_RESOURCES_PATH"  "$OLD_TEST_RESOURCES_PATH"  "$OLD_INTEGTEST_RESOURCES_PATH"  "$OLD_PACKAGE_ROOT" )
declare -a DEST_DIRS=( "$DEST_MAIN_PATH" "$DEST_TEST_PATH"   "$DEST_INTEGTEST_PATH" "$DEST_TESTFIXTURE_PATH" "$DEST_MAIN_RESOURCES_PATH" "$DEST_TEST_RESOURCES_PATH" "$DEST_INTEGTEST_RESOURCES_PATH" "$REMNANTS_ARCHIVE_PATH" )

for ((i=0;i<${#SOURCE_DIRS[@]};++i)); do
  # Check if source directory exists
  if [ -d "${SOURCE_DIRS[$i]}" ]; then
    echo -e "Moving '${PATH_DESC[$i]}' files (ignoring existing)... \n - From: ${SOURCE_DIRS[$i]}\n - To:   ${DEST_DIRS[$i]}"
    mkdir -p "${DEST_DIRS[$i]}"
    rsync -av --ignore-existing --remove-source-files "${SOURCE_DIRS[$i]}/" "${DEST_DIRS[$i]}/"
  else
    echo "The source directory does not exist: ${SOURCE_DIRS[$i]}     ('${PATH_DESC[$i]}')"
  fi
done

# Remove empty directories in CDK_ROOT
find "$CDK_ROOT/" -type d -empty -delete
# Remove empty directories in the OLD_PACKAGE_ROOT
find "$OLD_PACKAGE_ROOT/" -type d -empty -delete

# List remnant files in the OLD_PACKAGE_ROOT
echo "Files remaining in $OLD_PACKAGE_ROOT:"
find "$OLD_PACKAGE_ROOT" -type f

# Move remaining files in the OLD_PACKAGE_ROOT to the CDK 'archive' directory
# echo -e "Moving renaming files... \n - From: $OLD_PACKAGE_ROOT\n - To:   $ARCHIVE_ROOT"

# Ensure the parent directory exists
# mkdir -p "$ARCHIVE_ROOT/"

# # Move the entire remnants of the package root to the archived directory
# mv "$OLD_PACKAGE_ROOT/" "$ARCHIVE_ROOT/"

echo -e "Migration operation complete!\n"

for path in "$DEST_MAIN_PATH" "$DEST_TEST_PATH" "$DEST_INTEGTEST_PATH" "$DEST_TESTFIXTURE_PATH"; do
  echo "List of packages in $path:"
  find "$path" -name "*.java" -type f | while read -r file; do
    # Extract the package declaration from the file
    package=$(grep "^package " "$file" | cut -d " " -f 2- | sed 's/;$//')
    # Print the package declaration
    echo "$package"
  done | sort -u
  echo ""
done

# Post-processing
# 1. Add the cdk gradle plugin:
# Replace:        (id 'airbyte-integration-test-java')
# With:           $1\n.   id 'airbyte-java-cdk'
# Include Files:  build.gradle
# Exclude Files:  archive
# 2. Additional search-and-replace for 'standardtest'
# Replace:        io.airbyte.integrations.standardtest
# With:           io.airbyte.cdk.integrations.standardtest
# Include Files:  .java
# Exclude Files:  archive,_temp_migration_script.sh

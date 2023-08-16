#!/bin/bash

# This file is an audit tool for the migration.
# It may be deleted befor the PR is merged.
# Usage:
#   MIGRATE_SH=./airbyte-cdk/java/airbyte-cdk/_temp_migration_script.sh
#   $MIGRATE_SH <OLD_PACKAGE_ROOT> <SUBPACKAGE_PATH>
#
# Examples:
#   $MIGRATE_SH airbyte-db/db-lib db
#   $MIGRATE_SH airbyte-integrations/bases/base-java
#   $MIGRATE_SH airbyte-integrations/bases/base-java-s3
#   $MIGRATE_SH airbyte-integrations/bases/base-typing-deduping
#   $MIGRATE_SH airbyte-integrations/bases/base-typing-deduping-test
#   $MIGRATE_SH airbyte-integrations/bases/bases-destination-jdbc
#   $MIGRATE_SH airbyte-integrations/bases/debezium
#   $MIGRATE_SH airbyte-integrations/bases/s3-destination-base-integration-test
#   $MIGRATE_SH airbyte-integrations/bases/standard-destination-test
#   $MIGRATE_SH airbyte-integrations/bases/standard-source-test
#   $MIGRATE_SH airbyte-integrations/connectors/source-jdbc

# Other notes:
# - This script is idempotent. It should become a no-op if run to completion.
# - The "typing_deduping" and "typing_deduping_test" subpackages are special cases. They migrated from different directories while being declared as the same package name: "io.airbyte.integrations.destination.typing_deduping".

# Change these two lines for each new subpackage to move
OLD_PACKAGE_ROOT="$1"

# These lines should not need to be changed
OLD_SRC_PATH="$OLD_PACKAGE_ROOT/src/main/java/io/airbyte"
OLD_TEST_PATH="$OLD_PACKAGE_ROOT/src/test/java/io/airbyte"

CDK_ROOT="airbyte-cdk/java/airbyte-cdk"
DEST_MAIN="$CDK_ROOT/src/main/java/io/airbyte/cdk"
DEST_TEST="$CDK_ROOT/src/test/java/io/airbyte/cdk"

echo -e "Moving files (ignoring existing)... \n - From: $OLD_SRC_PATH\n - To:   $DEST_MAIN"
find "$OLD_SRC_PATH/" -type f | head
mkdir -p "$DEST_MAIN/"
rsync -av --ignore-existing --remove-source-files "$OLD_SRC_PATH/" "$DEST_MAIN/"

echo -e "Moving files (ignoring existing)... \n - From: $OLD_TEST_PATH\n - To:   $DEST_TEST"
find "$OLD_TEST_PATH/" -type f | head
mkdir -p "$DEST_TEST/"
rsync -av --ignore-existing --remove-source-files "$OLD_TEST_PATH/" "$DEST_TEST/"

# Remove empty directories in the OLD_PACKAGE_ROOT
find "$OLD_PACKAGE_ROOT/" -type d -empty -delete

# List remnant files in the OLD_PACKAGE_ROOT
echo "Files remaining in $OLD_PACKAGE_ROOT:"
find "$OLD_PACKAGE_ROOT/" -type f

# Move remaining files in the OLD_PACKAGE_ROOT to the CDK 'archive' directory
ARCHIVE_ROOT="airbyte-cdk/java/airbyte-cdk/archive"
echo -e "Moving files (ignoring existing)... \n - From: $OLD_PACKAGE_ROOT/\n - To:   $ARCHIVE_ROOT/"

# Ensure the parent directory exists
mkdir -p "$ARCHIVE_ROOT/"

# Move the entire remnants of `base-java` to the archived directory
mv "$OLD_PACKAGE_ROOT/" "$ARCHIVE_ROOT/"

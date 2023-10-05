#!/usr/bin/env python3
#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Migration script. TODO: Delete this script once the migration is complete.

Usage:
    python3 ./airbyte-cdk/java/airbyte-cdk/_temp_migration_script.py
    python3 ./airbyte-cdk/java/airbyte-cdk/_temp_migration_script.py test
"""

import os
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = "."
CDK_ROOT = f"{REPO_ROOT}/airbyte-cdk/java/airbyte-cdk"
EXCLUDE_DIRS = [
    "target",
    "out",
    "build",
    "dist",
    ".git",
    "docs",
    ".venv",
    "sample_files",
    "node_modules",
    "lib",
    "bin",
    "__pycache__",
    ".gradle",
    ".symlinks",
]
EXCLUDE_FILES = [
    "pom\.xml",
    "README\.md",
    "LICENSE",
    "build",
    ".coverage\..*",
    ".*\.zip",
    ".*\.gz",
    "_temp_.*",
    ".*\.dat",
    ".*\.bin",
    ".*\.csv",
    ".*\.jsonl",
    ".*\.png",
    ".*\.db",
    ".*\.pyc",
    ".*\.jar",
    ".*\.archive",
    ".*\.coverage",
]
CORE_FEATURE = "core"
DB_SOURCES_FEATURE = "db-sources"
DB_DESTINATIONS_FEATURE = "db-destinations"

MAIN_PACKAGES = {
    CORE_FEATURE: [
        "airbyte-db/db-lib",  # Jooq is fragile and reliant on manual code generation steps
        "airbyte-integrations/bases/base-java",
        "airbyte-integrations/bases/base-java-s3",
    ],
    DB_SOURCES_FEATURE: [
        "airbyte-integrations/bases/debezium",
        "airbyte-integrations/connectors/source-jdbc",
        "airbyte-integrations/connectors/source-relational-db",
    ],
    DB_DESTINATIONS_FEATURE: [
        "airbyte-integrations/bases/bases-destination-jdbc",
        # "airbyte-integrations/bases/base-typing-deduping",  # Excluded by request
    ],
}
TEST_FIXTURE_PACKAGES = {
    CORE_FEATURE: [],
    DB_SOURCES_FEATURE: [
        "airbyte-test-utils",
        "airbyte-integrations/bases/base-standard-source-test-file",
        "airbyte-integrations/bases/standard-source-test",
    ],
    DB_DESTINATIONS_FEATURE: [
        # "airbyte-integrations/bases/base-typing-deduping-test",  # Excluded by request
        "airbyte-integrations/bases/s3-destination-base-integration-test",
        "airbyte-integrations/bases/standard-destination-test",
    ],
}
TEST_CMDS = [
    # These should pass:
    # f"{REPO_ROOT}/./gradlew :airbyte-cdk:java:airbyte-cdk:build",
    # f"{REPO_ROOT}/./gradlew :airbyte-integrations:connectors:source-postgres:test --fail-fast",
    # f"{REPO_ROOT}/./gradlew :airbyte-integrations:connectors:source-bigquery:test --fail-fast",
    # f"{REPO_ROOT}/./gradlew :airbyte-integrations:connectors:destination-bigquery:test --fail-fast",
    # f"{REPO_ROOT}/./gradlew :airbyte-integrations:connectors:destination-snowflake:test --fail-fast",
    # f"{REPO_ROOT}/./gradlew :airbyte-integrations:connectors:destination-gcs:test --fail-fast",
    # f"{REPO_ROOT}/./gradlew :airbyte-integrations:bases:base-typing-deduping:build",
    # f"{REPO_ROOT}/./gradlew :airbyte-integrations:bases:base-typing-deduping-test:build",
    # Working on:
    # Failing:
    f"{REPO_ROOT}/./gradlew :airbyte-integrations:connectors:destination-postgres:test --fail-fast",  # Needs cdk plugin and extension settings.
    f"{REPO_ROOT}/./gradlew :airbyte-cdk:java:airbyte-cdk:integrationTest",  # Missing image for source-jdbc
    f"{REPO_ROOT}/./gradlew :airbyte-integrations:connectors:source-postgres:integrationTestJava",  # org.testcontainers.containers.ContainerLaunchException: Container startup failed for image postgres:13-alpine
    # "java.io.StreamCorruptedException: Overriding the global section with a specific one at line 3: Host *":
    f"{REPO_ROOT}/./gradlew :airbyte-integrations:connectors:source-postgres:integrationTestJava --tests=SshKeyPostgresSourceAcceptanceTest.testEntrypointEnvVar",
    # SshKeyPostgresSourceAcceptanceTest.testIdenticalFullRefreshes
    # SshKeyPostgresSourceAcceptanceTest.testIncrementalSyncWithState
    # SshPasswordPostgresSourceAcceptanceTest.testEntrypointEnvVar
    # SshPasswordPostgresSourceAcceptanceTest.testIdenticalFullRefreshes
    # SshPasswordPostgresSourceAcceptanceTest.testIncrementalSyncWithState
]


def move_files(source_dir, dest_dir, path_desc):
    if os.path.isdir(source_dir):
        print(f"Moving '{path_desc}' files (ignoring existing)...\n" f" - From: {source_dir}\n" f" - To:   {dest_dir}")
        os.makedirs(dest_dir, exist_ok=True)
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                src_file = os.path.join(root, file)
                sub_dir = os.path.relpath(root, source_dir)
                dst_file = os.path.join(dest_dir, sub_dir, file)

                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.move(src_file, dst_file)
    else:
        pass
        # print(f"The source directory does not exist: {source_dir} ('{path_desc}')")


def remove_empty_dirs(root_dir):
    for root, dirs, files in os.walk(root_dir, topdown=False):
        for dir in dirs:
            path = os.path.join(root, dir)
            if not os.listdir(path):
                os.rmdir(path)


def list_remnant_files(from_dir: str):
    # List remnant files in the OLD_PACKAGE_ROOT
    print(f"Files remaining in {from_dir}:")
    for root, dirs, files in os.walk(from_dir):
        for f in files:
            print(os.path.join(root, f))


def move_package(old_package_root: str, feature_name: str, as_test_fixture: bool):
    # Define source and destination directories
    old_main_path = os.path.join(old_package_root, "src/main/java/io/airbyte")
    old_test_path = os.path.join(old_package_root, "src/test/java/io/airbyte")
    old_integtest_path = os.path.join(old_package_root, "src/test-integration/java/io/airbyte")
    old_perftest_path = os.path.join(old_package_root, "src/test-performance/java/io/airbyte")
    old_testfixture_path = os.path.join(old_package_root, "src/testfixtures/java/io/airbyte")
    old_main_resources_path = os.path.join(old_package_root, "src/main/resources")
    old_test_resources_path = os.path.join(old_package_root, "src/test/resources")
    old_integtest_resources_path = os.path.join(old_package_root, "src/test-integration/resources")
    old_perftest_resources_path = os.path.join(old_package_root, "src/test-performance/resources")
    old_testfixture_resources_path = os.path.join(old_package_root, "src/testfixtures/resources")

    dest_main_path = os.path.join(CDK_ROOT, feature_name, "src/main/java/io/airbyte/cdk")
    dest_test_path = os.path.join(CDK_ROOT, feature_name, "src/test/java/io/airbyte/cdk")
    dest_integtest_path = os.path.join(CDK_ROOT, feature_name, "src/test-integration/java/io/airbyte/cdk")
    dest_perftest_path = os.path.join(CDK_ROOT, feature_name, "src/test-performance/java/io/airbyte/cdk")
    dest_testfixture_path = os.path.join(CDK_ROOT, feature_name, "src/testFixtures/java/io/airbyte/cdk")

    old_project_name = str(Path(old_package_root).parts[-1])
    remnants_archive_path = os.path.join(CDK_ROOT, "archive", old_project_name)

    dest_main_resources_path = os.path.join(CDK_ROOT, feature_name, "src/main/resources")
    dest_test_resources_path = os.path.join(CDK_ROOT, feature_name, "src/test/resources")
    dest_integtest_resources_path = os.path.join(CDK_ROOT, feature_name, "src/test-integration/resources")
    dest_perftest_resources_path = os.path.join(CDK_ROOT, feature_name, "src/test-performance/resources")
    dest_testfixture_resources_path = os.path.join(CDK_ROOT, feature_name, "src/testFixtures/resources")

    if as_test_fixture:
        # Move the test project's 'main' files to the test fixtures directory
        dest_main_path = dest_testfixture_path
        dest_main_resources_path = dest_testfixture_resources_path

    # Define source and destination directories as list of tuples
    paths = [
        ("main classes", old_main_path, dest_main_path),
        ("main test classes", old_test_path, dest_test_path),
        ("integ test classes", old_integtest_path, dest_integtest_path),
        ("perf test classes", old_perftest_path, dest_perftest_path),
        ("test fixtures", old_testfixture_path, dest_testfixture_path),
        ("main resources", old_main_resources_path, dest_main_resources_path),
        ("test resources", old_test_resources_path, dest_test_resources_path),
        ("integ test resources", old_integtest_resources_path, dest_integtest_resources_path),
        ("perf test resources", old_perftest_resources_path, dest_perftest_resources_path),
        ("test fixtures resources", old_testfixture_resources_path, dest_testfixture_resources_path),
        ("remnants to archive", old_package_root, remnants_archive_path),
    ]
    for path_desc, source_dir, dest_dir in paths:
        move_files(source_dir, dest_dir, path_desc)
    remove_empty_dirs(old_package_root)


def migrate_package_refs(
    text_pattern: str,
    text_replacement: str,
    within_dir: str,
    exclude_files: list,
    exclude_dirs: list,
):
    """
    Migrates a Java package to the new CDK package structure.

    Args:
        package_root (str): The root directory of the package to migrate.
        exclude_files (list): A list of file patterns to exclude from the migration.
        exclude_dirs (list): A list of directory patterns to exclude from the migration.

    Returns:
        None
    """
    # Define the files to exclude from the search
    exclude_files_pattern = "|".join(exclude_files)
    exclude_files_regex = re.compile(exclude_files_pattern)

    # Walk the directory tree and perform the find and replace operation on each file
    for root, dirs, files in os.walk(within_dir):
        # Exclude files that match the exclude_files pattern
        files = [f for f in files if not exclude_files_regex.match(f)]

        for file in files:
            file_path = os.path.join(root, file)
            if any([exclude_dir in file_path.split("/") for exclude_dir in exclude_dirs]):
                continue

            # print("Scanning file: ", file_path)
            # Exclude files that match the exclude_files pattern
            if exclude_files_regex.match(file):
                continue

            # Read the file contents
            with open(file_path, "r") as f:
                try:
                    contents = f.read()
                except UnicodeDecodeError:
                    print(f"Skipping file {file_path} due to UnicodeDecodeError")
                    continue

            # Perform the find and replace operation
            new_contents = re.sub(text_pattern, text_replacement, contents)

            # Write back the file if it has changed
            if contents != new_contents:
                # Write the updated contents back to the file
                with open(file_path, "w") as f:
                    f.write(new_contents)
        # else:
        #     print(f"No files found to scan within {within_dir}")


def update_cdk_package_defs() -> None:
    """Within CDK_ROOT, packages should be declared as 'package io.airbyte.cdk...'"""
    migrate_package_refs(
        text_pattern=r"package io\.airbyte\.(?!cdk\.)(?!cdk$)",
        text_replacement=r"package io.airbyte.cdk.",
        within_dir=CDK_ROOT,
        exclude_files=EXCLUDE_FILES,
        exclude_dirs=EXCLUDE_DIRS,
    )
    # Undo any dupes if they exist.
    migrate_package_refs(
        text_pattern=r"package io\.airbyte\.cdk\.cdk",
        text_replacement=r"package io.airbyte.cdk",
        within_dir=CDK_ROOT,
        exclude_files=EXCLUDE_FILES,
        exclude_dirs=EXCLUDE_DIRS,
    )


def refactor_cdk_package_refs() -> None:
    for text_pattern, text_replacement, within_dir in [
        (
            r"(?<!package )io\.airbyte\.(db)",
            r"io.airbyte.cdk.\1",
            REPO_ROOT,
        ),
        (
            r"(?<!package )io\.airbyte\.(?!.*typing_deduping)(integrations\.base|integrations\.debezium|integrations\.standardtest|integrations\.destination\.NamingConventionTransformer|integrations\.destination\.StandardNameTransformer|integrations\.destination\.jdbc|integrations\.destination\.record_buffer|integrations\.destination\.normalization|integrations\.destination\.buffered_stream_consumer|integrations\.destination\.dest_state_lifecycle_manager|integrations\.destination\.staging|integrations\.destination_async|integrations\.source\.jdbc|integrations\.source\.relationaldb|integrations\.util|integrations\.BaseConnector|test\.utils)",
            r"io.airbyte.cdk.\1",
            REPO_ROOT,
        ),
        (
            r"(?<!package )io\.airbyte\.integrations\.destination\.s3\.(avro|constant|credential|csv|jsonl|parquet|S3BaseChecks|S3ConsumerFactory|S3DestinationConfig|S3DestinationConstants|S3Format|S3FormatConfig|S3FormatConfigs|SerializedBufferFactory|StorageProvider|S3StorageOperations|template|util|writer)\b",
            r"io.airbyte.cdk.integrations.destination.s3.\1",
            REPO_ROOT,
        ),
    ]:
        migrate_package_refs(
            text_pattern,
            text_replacement,
            within_dir=within_dir,
            exclude_files=EXCLUDE_FILES,
            exclude_dirs=EXCLUDE_DIRS,
        )


def main() -> None:
    # Remove empty directories in CDK_ROOT
    remove_empty_dirs(CDK_ROOT)

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            for cmd in TEST_CMDS:
                print(f"Running test command: {cmd}")
                exit_code = os.system(cmd)
                if exit_code != 0:
                    print(f"Error running command: {cmd}")
                    sys.exit(exit_code)
            return
        else:
            raise ValueError(f"Unknown argument: {sys.argv[1]}")

    for feature_name in MAIN_PACKAGES.keys():
        paths_to_migrate = MAIN_PACKAGES[feature_name] + TEST_FIXTURE_PACKAGES[feature_name]
        for old_package_root in paths_to_migrate:
            # Remove empty directories in the OLD_PACKAGE_ROOT
            as_test_fixture = old_package_root in TEST_FIXTURE_PACKAGES[feature_name]
            move_package(old_package_root, feature_name, as_test_fixture)
            remove_empty_dirs(old_package_root)
            update_cdk_package_defs()

    refactor_cdk_package_refs()

    # Move the base-java folder back, as base docker image definition for java connectors:
    move_files(
        source_dir="airbyte-cdk/java/airbyte-cdk/archive/base-java",
        dest_dir="airbyte-integrations/bases/base-java",
        path_desc="base java dockerfile definitions (moving back)",
    )

    print("Migration operation complete!")


if __name__ == "__main__":
    main()

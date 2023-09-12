import os
import re
import shutil
from pathlib import Path
import sys

REPO_ROOT = "."
CDK_ROOT = f"{REPO_ROOT}/airbyte-cdk/java/airbyte-cdk"

def move_files(source_dir, dest_dir, path_desc):
    if os.path.isdir(source_dir):
        print(f"Moving '{path_desc}' files (ignoring existing)...\n - From: {source_dir}\n - To:   {dest_dir}")
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
    else:
        print(f"The source directory does not exist: {source_dir} ('{path_desc}')")

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

def move_package(old_package_root):
    # Define source and destination directories
    old_main_path = os.path.join(old_package_root, "src/main/java/io/airbyte")
    old_test_path = os.path.join(old_package_root, "src/test/java/io/airbyte")
    old_integtest_path = os.path.join(old_package_root, "src/test-integration/java/io/airbyte")
    old_testfixture_path = os.path.join(old_package_root, "src/testfixtures/java/io/airbyte")
    old_main_resources_path = os.path.join(old_package_root, "src/main/resources")
    old_test_resources_path = os.path.join(old_package_root, "src/test/resources")
    old_integtest_resources_path = os.path.join(old_package_root, "src/test-integration/resources")

    dest_main_path = os.path.join(CDK_ROOT, "src/main/java/io/airbyte/cdk")
    dest_test_path = os.path.join(CDK_ROOT, "src/test/java/io/airbyte/cdk")
    dest_integtest_path = os.path.join(CDK_ROOT, "src/test-integration/java/io/airbyte/cdk")
    dest_testfixture_path = os.path.join(CDK_ROOT, "src/testFixtures/java/io/airbyte/cdk")

    old_project_name = str(Path(old_package_root).parts[-1])
    dest_main_resources_path = os.path.join(CDK_ROOT, "src/main/resources", old_project_name)
    dest_test_resources_path = os.path.join(CDK_ROOT, "src/test/resources", old_project_name)
    dest_integtest_resources_path = os.path.join(CDK_ROOT, "src/test-integration/resources", old_project_name)
    remnants_archive_path = os.path.join(CDK_ROOT, "archive", old_project_name)

    # Define source and destination directories as lists

    paths = [
        ("main classes", old_main_path, dest_main_path),
        ("main test classes", old_test_path, dest_test_path),
        ("integ test classes", old_integtest_path, dest_integtest_path),
        ("test fixtures", old_testfixture_path, dest_testfixture_path),
        ("main resources", old_main_resources_path, dest_main_resources_path),
        ("test resources", old_test_resources_path, dest_test_resources_path),
        ("integ test resources", old_integtest_resources_path, dest_integtest_resources_path),
        ("remnants to archive", old_package_root, remnants_archive_path)
    ]

    remove_empty_dirs(old_package_root)
    for path_desc, source_dir, dest_dir in paths:
        move_files(source_dir, dest_dir, path_desc)
    remove_empty_dirs(old_package_root)


def migrate_package_refs(
    text_pattern: str,
    text_replacement: str,
    within_dir: str,
    exclude_files: list,
    exclude_dirs: list,
    include_dirs: list,
):
    """
    Migrates a Java package to the new CDK package structure.

    Args:
        package_root (str): The root directory of the package to migrate.
        exclude_files (list): A list of file patterns to exclude from the migration.
        exclude_dirs (list): A list of directory patterns to exclude from the migration.
        include_dirs (list): A list of directory patterns to include in the migration.

    Returns:
        None
    """

    # Define the directories to include in the search
    search_dirs = [os.path.join(within_dir, d) for d in include_dirs]

    # Define the files to exclude from the search
    exclude_files_pattern = "|".join(exclude_files)
    exclude_files_regex = re.compile(exclude_files_pattern)

    # Define the directories to exclude from the search
    exclude_dirs_pattern = "|".join(exclude_dirs)
    exclude_dirs_regex = re.compile(exclude_dirs_pattern)

    # Walk the directory tree and perform the find and replace operation on each file
    for root, dirs, files in os.walk(within_dir):
        # Exclude directories that match the exclude_dirs pattern
        dirs = [d for d in dirs if not exclude_dirs_regex.match(d)]

        # Exclude files that match the exclude_files pattern
        files = [f for f in files if not exclude_files_regex.match(f)]

        # Only search directories that are included in the search_dirs list
        if root not in search_dirs:
            continue

        for file in files:
            # Exclude files that match the exclude_files pattern
            if exclude_files_regex.match(file):
                continue

            # Read the file contents
            file_path = os.path.join(root, file)
            with open(file_path, "r") as f:
                contents = f.read()

            # Perform the find and replace operation
            new_contents = re.sub(text_pattern, text_replacement, contents)

            # Write the updated contents back to the file
            with open(file_path, "w") as f:
                f.write(new_contents)


def migrate_all_packages_refs() -> None:
    for text_pattern, text_replacement, within_dir, exclude_dirs in [
        (
            r"package io\.airbyte\.(?<!\.cdk)",
            r"package io.airbyte.cdk.",
            CDK_ROOT,
            ["target", "out", "build", "dist", "node_modules", "lib", "bin"]
        ),
        (
            r"(?<!package )io\.airbyte\.(db|integrations\.base|integrations\.debezium|integrations\.destination\.NamingConventionTransformer|integrations\.destination\.StandardNameTransformer|integrations\.destination\.jdbc|integrations\.destination\.record_buffer|integrations\.destination\.normalization|integrations\.destination\.buffered_stream_consumer|integrations\.destination\.dest_state_lifecycle_manager|integrations\.destination\.staging|integrations\.destination_async|integrations\.source\.jdbc|integrations\.source\.relationaldb|integrations\.util|integrations\.BaseConnector|test\.utils)",
            r"io.airbyte.cdk.\2",
            REPO_ROOT,
            ["target", "out", "build", "dist", "node_modules", "lib", "bin", CDK_ROOT]
        )
    ]:
        migrate_package_refs(
            text_pattern,
            text_replacement,
            within_dir=within_dir,
            exclude_files=["pom.xml", "README.md", "LICENSE"],
            exclude_dirs=exclude_dirs,
            include_dirs=["src"],
        )


def main() -> None:
    # Remove empty directories in CDK_ROOT
    remove_empty_dirs(CDK_ROOT)

    # Check if there was a CLI argument passed
    paths_to_migrate: list[str] = []
    if len(sys.argv) > 1:
        paths_to_migrate = [sys.argv[1]]

    for old_package_root in paths_to_migrate:
        # Remove empty directories in the OLD_PACKAGE_ROOT
        move_package(old_package_root)
        remove_empty_dirs(old_package_root)

    # Move remaining files in the OLD_PACKAGE_ROOT to the CDK 'archive' directory
    # print(f"Moving renaming files...\n - From: {OLD_PACKAGE_ROOT}\n - To:   {REMNANTS_ARCHIVE_PATH}")
    # os.makedirs(REMNANTS_ARCHIVE_PATH, exist_ok=True)
    # shutil.move(OLD_PACKAGE_ROOT, REMNANTS_ARCHIVE_PATH)

    print("Migration operation complete!")


if __name__ == "__main__":
    main()


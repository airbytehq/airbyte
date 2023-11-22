# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

# This script takes an arg with a connector selector, then bumps the CDK version of all connectors that match that selector
# Example: python tools/bin/bump_cdk.py --selector=source-s3 <- this targets the s3 source connector
# Example: python tools/bin/bump_cdk.py --selector=connectorSubtype:vectorstore <- this targets all connectors with subtype vectorstore
# Example: python tools/bin/bump_cdk.py --selector=connectorSubtype:vectorstore,source-s3 <- this targets all connectors with subtype vectorstore and the s3 source connector

# Step 1: Get the connector selector from the command line

import argparse
import os
import re
import subprocess
import sys
import datetime

parser = argparse.ArgumentParser(description="Bump CDK version for connectors")
parser.add_argument("--selector", required=True, help="Connector selector")
parser.add_argument("--pr", required=False, help="PR Number")
parser.add_argument("--version", required=True, help="New CDK version number")
parser.add_argument("--changelog", required=False, help="Changelog entry")
args = parser.parse_args()

# store the selector in a variable
selector = args.selector

# Split the selector into an array by comma, then turn into key value pairs (if there is a colon, split on that, otherwise the value is the value and the key is connector)
# Example: source-s3 -> {name: source-s3}
# Example: connectorSubtype:vectorstore -> {connectorSubtype: vectorstore}
# Example: connectorSubtype:vectorstore,source-s3 -> {connectorSubtype: vectorstore, name: source-s3}
# Example: connectorSubtype:vectorstore,source-s3,connectorSubtype:vectorstore -> {connectorSubtype: vectorstore, name: source-s3, connectorSubtype: vectorstore}

# Split the selector into an array by comma
selectorArray = selector.split(",")
# Create a new array to store the key value pairs
selectorArrayKeyValue = []
# Loop through the selector array
for selector in selectorArray:
    # If the selector has a colon, split on that
    if ":" in selector:
        selectorKeyValue = selector.split(":")
        selectorArrayKeyValue.append({selectorKeyValue[0]: selectorKeyValue[1]})
    # Otherwise, the key is name and the value is the selector
    else:
        selectorArrayKeyValue.append({"connector": selector})

# Get all folders in airbyte-integrations/connectors
connectorFolders = os.listdir("./airbyte-integrations/connectors")

connectors_to_bump = []

# Loop through the connector folders and read the metadata.yaml file as object
for connectorFolder in connectorFolders:
    # Get the manifest file path
    manifestFilePath = f"./airbyte-integrations/connectors/{connectorFolder}/metadata.yaml"
    # Check if the manifest file exists
    if os.path.exists(manifestFilePath):
        # Read the manifest file as object
        manifestFile = open(manifestFilePath, "r")
        manifestFileObject = manifestFile.read()
        manifestFile.close()
        # Loop through the selector array key value pairs
        for selector in selectorArrayKeyValue:
            # Loop through the key value pairs
            for key, value in selector.items():
                # If the key is connector, check if the connector name matches the value
                if key == "connector":
                    if connectorFolder == value:
                        connectors_to_bump.append(connectorFolder)
                # If the key is connectorSubtype, check if the connectorSubtype matches the value
                # TODO use actual yaml parsing for this
                elif re.search(f"{key}: {value}", manifestFileObject):
                    connectors_to_bump.append(connectorFolder)

print("Found connectors to bump:")
print(connectors_to_bump)

current_cdk_version = args.version

print(f"New CDK version: {current_cdk_version}")

# Step 2: Bump the CDK version for each connector
# To bump the CDK version, do the following:
# * Check if there is a setup.py file in the connector folder
# * If there is, read the setup.py file as object
# * Find  a string that describes the airbyte-cdk dependency. It might have an extra definition after it, like [file-based], or a version specification like >=0.53.5 or both
# * If there is no version, add the version >=0.53.5
# * If there is a version, bump it to 0.53.5 (leave >= or == or whatever in place)

# Loop through the connectors to bump
for connector in connectors_to_bump:
    # Get the setup file path
    setupFilePath = f"./airbyte-integrations/connectors/{connector}/setup.py"
    # Check if the setup file exists
    if os.path.exists(setupFilePath):
        # Read the setup file as object
        setupFile = open(setupFilePath, "r")
        setupFileObject = setupFile.read()
        setupFile.close()
        # Find the airbyte-cdk dependency
        airbyte_cdk_dependency = re.search(
            r"airbyte-cdk(?P<extra>\[[a-zA-Z0-9-]*\])?(?P<version>[<>=!~]+[0-9]*\.[0-9]*\.[0-9]*)?", setupFileObject
        )
        # If there is no airbyte-cdk dependency, add the version
        if airbyte_cdk_dependency is not None:

            new_version = f"airbyte-cdk{airbyte_cdk_dependency.group('extra') or ''}=={current_cdk_version}"
            setupFileObject = setupFileObject.replace(airbyte_cdk_dependency.group(), new_version)
            print(f"Updated {connector}")
        else:
            print(f"No airbyte-cdk dependency found, skipping {connector}")
            continue
        # Write the setup file
        setupFile = open(setupFilePath, "w")
        setupFile.write(setupFileObject)
        setupFile.close()

        if args.pr and args.changelog:
            # Bump version in metadata.yaml:
            # * Read metadata.yaml
            # * Get current version (field is dockerImageTag: )
            # * Bump the patch version
            # * Write metadata.yaml back

            # Get the manifest file path
            manifestFilePath = f"./airbyte-integrations/connectors/{connector}/metadata.yaml"
            manifestFile = open(manifestFilePath, "r")
            manifestFileObject = manifestFile.read()
            manifestFile.close()

            # Get the current version
            current_version = re.search(r"dockerImageTag: (?P<version>[0-9]*\.[0-9]*\.[0-9]*)", manifestFileObject)
            if current_version is not None:
                # Split by ., then bump the last number
                version_numbers = current_version.group("version").split(".")
                version_numbers[-1] = str(int(version_numbers[-1]) + 1)
                new_version = ".".join(version_numbers)
                manifestFileObject = manifestFileObject.replace(current_version.group(), f"dockerImageTag: {new_version}")
                # write back
                manifestFile = open(manifestFilePath, "w")
                manifestFile.write(manifestFileObject)
                manifestFile.close() 

                # if there is a Dockerfile, bump the version there too (line starts with LABEL io.airbyte.version=)
                dockerFilePath = f"./airbyte-integrations/connectors/{connector}/Dockerfile"
                if os.path.exists(dockerFilePath):
                    dockerFile = open(dockerFilePath, "r")
                    dockerFileObject = dockerFile.read()
                    dockerFile.close()
                    dockerFileObject = re.sub(r"LABEL io.airbyte.version=.*", f"LABEL io.airbyte.version={new_version}", dockerFileObject)
                    # write back
                    dockerFile = open(dockerFilePath, "w")
                    dockerFile.write(dockerFileObject)
                    dockerFile.close() 
            else:
                print(f"No dockerImageTag found, skipping bumping tag for {connector}")

            # Add changelog entry in documentation file:
            # * Read documentation file (docs/source|destination/{connector-name}.md)
            # * Find the changelog table (line with "| Version | Date")
            # * Add a new line with the new version, date, and changelog entry
            # * Write documentation file back

            # Get the documentation file path
            just_the_name = connector.replace("source-", "").replace("destination-", "")
            documentationFilePath = f"./docs/integrations/sources/{just_the_name}.md" if os.path.exists(
                f"./docs/integrations/sources/{just_the_name}.md"
            ) else f"./docs/integrations/destinations/{just_the_name}.md"

            documentationFile = open(documentationFilePath, "r")
            documentationFileObject = documentationFile.read()
            documentationFile.close()

            # Find the changelog table
            changelog_table = re.search(r"\| Version \| Date.*\n.*\n", documentationFileObject)
            if changelog_table is not None:
                # Add a new line with the new version, date, and changelog entry
                new_changelog_entry = f"| {new_version} | {datetime.datetime.now().strftime('%Y-%m-%d')} | [{args.pr}](https://github.com/airbytehq/airbyte/pull/{args.pr}) | {args.changelog} |\n"
                documentationFileObject = documentationFileObject.replace(
                    changelog_table.group(), f"{changelog_table.group()}\n{new_changelog_entry}"
                )
            else:
                print(f"No changelog table found, skipping adding changelog entry for {connector}")
            
            # write back
            documentationFile = open(documentationFilePath, "w")
            documentationFile.write(documentationFileObject)
            documentationFile.close()
    else:
        print(f"No setup.py found, skipping {connector}")

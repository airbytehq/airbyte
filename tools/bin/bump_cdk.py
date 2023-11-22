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

parser = argparse.ArgumentParser(description='Bump CDK version for connectors')
parser.add_argument('--selector', required=True, help='Connector selector')
parser.add_argument('--pr', required=False, help='PR Number')
parser.add_argument('--version', required=True, help='New CDK version number')
parser.add_argument('--changelog', required=False, help='Changelog entry')
args = parser.parse_args()

# store the selector in a variable
selector = args.selector

# Split the selector into an array by comma, then turn into key value pairs (if there is a colon, split on that, otherwise the value is the value and the key is connector)
# Example: source-s3 -> {name: source-s3}
# Example: connectorSubtype:vectorstore -> {connectorSubtype: vectorstore}
# Example: connectorSubtype:vectorstore,source-s3 -> {connectorSubtype: vectorstore, name: source-s3}
# Example: connectorSubtype:vectorstore,source-s3,connectorSubtype:vectorstore -> {connectorSubtype: vectorstore, name: source-s3, connectorSubtype: vectorstore}

# Split the selector into an array by comma
selectorArray = selector.split(',')
# Create a new array to store the key value pairs
selectorArrayKeyValue = []
# Loop through the selector array
for selector in selectorArray:
    # If the selector has a colon, split on that
    if ':' in selector:
        selectorKeyValue = selector.split(':')
        selectorArrayKeyValue.append({selectorKeyValue[0]: selectorKeyValue[1]})
    # Otherwise, the key is name and the value is the selector
    else:
        selectorArrayKeyValue.append({'connector': selector})

# Get all folders in airbyte-integrations/connectors
connectorFolders = os.listdir('./airbyte-integrations/connectors')

connectors_to_bump = []

# Loop through the connector folders and read the metadata.yaml file as object
for connectorFolder in connectorFolders:
    # Get the manifest file path
    manifestFilePath = f'./airbyte-integrations/connectors/{connectorFolder}/metadata.yaml'
    # Check if the manifest file exists
    if os.path.exists(manifestFilePath):
        # Read the manifest file as object
        manifestFile = open(manifestFilePath, 'r')
        manifestFileObject = manifestFile.read()
        manifestFile.close()
        # Loop through the selector array key value pairs
        for selector in selectorArrayKeyValue:
            # Loop through the key value pairs
            for key, value in selector.items():
                # If the key is connector, check if the connector name matches the value
                if key == 'connector':
                    if connectorFolder == value:
                        connectors_to_bump.append(connectorFolder)
                # If the key is connectorSubtype, check if the connectorSubtype matches the value
                # TODO use actual yaml parsing for this
                elif re.search(f'{key}: {value}', manifestFileObject):
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
    setupFilePath = f'./airbyte-integrations/connectors/{connector}/setup.py'
    # Check if the setup file exists
    if os.path.exists(setupFilePath):
        # Read the setup file as object
        setupFile = open(setupFilePath, 'r')
        setupFileObject = setupFile.read()
        setupFile.close()
        # Find the airbyte-cdk dependency
        airbyte_cdk_dependency = re.search(r'airbyte-cdk(?P<extra>\[[a-zA-Z0-9-]*\])?(?P<version>[<>=!~]+[0-9]*\.[0-9]*\.[0-9]*)?', setupFileObject)
        # If there is no airbyte-cdk dependency, add the version
        if airbyte_cdk_dependency is not None:

            new_version = f"airbyte_cdk{airbyte_cdk_dependency.group('extra') or ''}=={current_cdk_version}"
            setupFileObject = setupFileObject.replace(airbyte_cdk_dependency.group(), new_version)
            print(f"Updated {connector}")
        else:
            print(f"No airbyte-cdk dependency found, skipping {connector}")
        # Write the setup file
        setupFile = open(setupFilePath, 'w')
        setupFile.write(setupFileObject)
        setupFile.close()

        if args.pr and args.changelog:
            # Bump connector version via airbyte-ci = airbyte-ci connectors --name={connector} bump_version patch {pr number from args} "Update CDK version: {changelog from args}"
            subprocess.run(f"airbyte-ci connectors --name={connector} bump_version patch {args.pr} \"Update CDK version: {args.changelog}\"", shell=True)
    else:
        print(f"No setup.py found, skipping {connector}")